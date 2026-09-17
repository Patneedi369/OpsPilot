import asyncio
import sys
import unittest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.persistence.session import SessionLocal, engine
from app.main import app
from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.schemas.telemetry import TelemetrySignalIngest
from app.services.audit_service import log_audit, query_audit_logs
from app.services.auth_service import authenticate_user, create_token, decode_token
from app.services.detection_service import evaluate_and_correlate, ingest_signal


class TestPhases12And13(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        await engine.dispose()

    async def test_01_valid_signal_ingestion(self):
        """Test 1: Ingesting a valid telemetry signal saves it as active."""
        async with SessionLocal() as session:
            payload = TelemetrySignalIngest(
                metric="api_latency_ms",
                value=550.0,
                threshold=500.0,
                service_id="user-service",
                source="prometheus",
            )
            sig = await ingest_signal(session, payload)
            self.assertIsNotNone(sig.id)
            self.assertEqual(sig.metric, "api_latency_ms")
            self.assertEqual(sig.value, 550.0)
            self.assertEqual(sig.status, "active")

    async def test_02_threshold_breach_creates_incident(self):
        """Test 2: Signal breaching threshold creates a new incident & detection event."""
        async with SessionLocal() as session:
            payload = TelemetrySignalIngest(
                metric="5xx_error_rate",
                value=12.5,
                threshold=1.0,
                service_id="payment-service",
                source="datadog",
            )
            sig = await ingest_signal(session, payload)
            events = await evaluate_and_correlate(session, service_id="payment-service", auto_investigate=False)
            self.assertGreaterEqual(len(events), 1)
            evt = events[0]
            self.assertIsNotNone(evt.incident_id)
            self.assertIn("payment-service", evt.summary)

            inc_res = await session.execute(select(Incident).where(Incident.id == evt.incident_id))
            inc = inc_res.scalars().first()
            self.assertIsNotNone(inc)
            self.assertEqual(inc.service_id, "payment-service")

    async def test_03_related_signals_correlate_one_incident(self):
        """Test 3: Multiple related signals for same service correlate into one single incident."""
        async with SessionLocal() as session:
            svc = "inventory-service"
            await ingest_signal(session, TelemetrySignalIngest(metric="api_latency_ms", value=900.0, threshold=500.0, service_id=svc))
            await ingest_signal(session, TelemetrySignalIngest(metric="db_query_duration_ms", value=1200.0, threshold=50.0, service_id=svc))
            await ingest_signal(session, TelemetrySignalIngest(metric="pool_utilization", value=95.0, threshold=80.0, service_id=svc))

            events = await evaluate_and_correlate(session, service_id=svc, auto_investigate=False)
            self.assertEqual(len(events), 1)
            evt = events[0]
            self.assertEqual(evt.correlated_signals_count, 3)

    async def test_04_duplicate_active_signal_does_not_create_duplicate_incident(self):
        """Test 4: Ingesting new breaching signal while incident is active attaches to existing incident."""
        async with SessionLocal() as session:
            svc = "auth-service"
            await ingest_signal(session, TelemetrySignalIngest(metric="5xx_error_rate", value=5.0, threshold=1.0, service_id=svc))
            events1 = await evaluate_and_correlate(session, service_id=svc, auto_investigate=False)
            inc_id_1 = events1[0].incident_id

            await ingest_signal(session, TelemetrySignalIngest(metric="api_latency_ms", value=800.0, threshold=500.0, service_id=svc))
            events2 = await evaluate_and_correlate(session, service_id=svc, auto_investigate=False)
            inc_id_2 = events2[0].incident_id

            self.assertEqual(inc_id_1, inc_id_2)

    async def test_05_inc2043_signals_correlate_correctly(self):
        """Test 5: Telemetry signals for INC-2043 (deploy, slow query, pool pressure, API 5xx) correlate to INC-2043."""
        async with SessionLocal() as session:
            svc = "orders-service"
            await ingest_signal(session, TelemetrySignalIngest(metric="deployment_event", value=1.0, threshold=0.0, service_id=svc, metadata={"deploy_id": "deploy-4821"}))
            await ingest_signal(session, TelemetrySignalIngest(metric="db_query_duration_ms", value=4500.0, threshold=50.0, service_id=svc))
            await ingest_signal(session, TelemetrySignalIngest(metric="pool_utilization", value=98.0, threshold=80.0, service_id=svc))
            await ingest_signal(session, TelemetrySignalIngest(metric="5xx_error_rate", value=18.4, threshold=1.0, service_id=svc))

            events = await evaluate_and_correlate(session, service_id=svc, auto_investigate=False)
            self.assertGreaterEqual(len(events), 1)
            self.assertEqual(events[0].incident_id, "INC-2043")

    async def test_06_detection_auto_triggers_investigation(self):
        """Test 6: Detection with auto_investigate=True triggers investigation workflow."""
        async with SessionLocal() as session:
            svc = "notification-service"
            await ingest_signal(session, TelemetrySignalIngest(metric="5xx_error_rate", value=25.0, threshold=1.0, service_id=svc))
            events = await evaluate_and_correlate(session, service_id=svc, auto_investigate=True)
            self.assertEqual(len(events), 1)
            inc_res = await session.execute(select(Incident).where(Incident.id == events[0].incident_id))
            inc = inc_res.scalars().first()
            self.assertIn(inc.status, ["investigating", "awaiting_approval"])

    async def test_07_authentication_success_and_failure(self):
        """Test 7: Auth succeeds with valid credentials and fails with invalid credentials."""
        async with SessionLocal() as session:
            user = await authenticate_user(session, "sre_user", "sre_password")
            self.assertIsNotNone(user)
            self.assertEqual(user.role, "SRE")

            token = create_token(user.id, user.username, user.role)
            payload = decode_token(token)
            self.assertIsNotNone(payload)
            self.assertEqual(payload["username"], "sre_user")

            invalid_user = await authenticate_user(session, "sre_user", "wrong_password")
            self.assertIsNone(invalid_user)

    async def test_08_sre_permissions(self):
        """Test 8: SRE role can access protected investigation endpoints."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/incidents/INC-2043/investigate",
                headers={"X-User-Role": "SRE", "X-User-Name": "sre_user"},
            )
            self.assertEqual(resp.status_code, 200)

    async def test_09_lead_permissions(self):
        """Test 9: Lead role can access audit logs endpoint."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/audit/logs",
                headers={"X-User-Role": "Lead", "X-User-Name": "lead_user"},
            )
            self.assertEqual(resp.status_code, 200)

    async def test_10_viewer_permission_denied(self):
        """Test 10: Viewer role receives 403 Forbidden when attempting to run investigation."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/incidents/INC-2043/investigate",
                headers={"X-User-Role": "Viewer", "X-User-Name": "viewer_user"},
            )
            self.assertEqual(resp.status_code, 403)
            self.assertIn("Permission denied", resp.json()["detail"])

    async def test_11_unauthorized_api_rejection(self):
        """Test 11: Invalid authentication bearer token is rejected with 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/incidents/INC-2043/investigate",
                headers={"Authorization": "Bearer invalid.token.value"},
            )
            self.assertEqual(resp.status_code, 401)

    async def test_12_audit_record_created_for_important_actions(self):
        """Test 12: log_audit creates immutable record in audit_logs table."""
        async with SessionLocal() as session:
            record = await log_audit(
                session=session,
                user_id="usr-sre-001",
                username="sre_user",
                user_role="SRE",
                action="test.action",
                resource_type="test_resource",
                resource_id="res-123",
                outcome="success",
            )
            self.assertIsNotNone(record.id)
            db_rec = await session.get(AuditLog, record.id)
            self.assertIsNotNone(db_rec)
            self.assertEqual(db_rec.action, "test.action")

    async def test_13_audit_records_can_be_queried_and_filtered(self):
        """Test 13: query_audit_logs filters audit logs correctly."""
        async with SessionLocal() as session:
            action_name = "filter.test.action"
            await log_audit(
                session=session,
                user_id="usr-lead-001",
                username="lead_user",
                user_role="Lead",
                action=action_name,
                resource_type="incident",
                resource_id="INC-2043",
                outcome="success",
            )
            results = await query_audit_logs(session, action=action_name, incident_id="INC-2043")
            self.assertGreaterEqual(len(results), 1)
            self.assertEqual(results[0].action, action_name)
