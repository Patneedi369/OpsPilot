import asyncio
import sys
import unittest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.core.logging import sanitize_val
from app.persistence.session import SessionLocal, engine
from app.main import app
from app.services.investigation_service import start_investigation_run


class TestPhases14And15(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        await engine.dispose()

    async def test_01_consistent_api_error_handling(self):
        """Test 1: HTTP exceptions return consistent JSON structure with detail, code, and request_id."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/incidents/INC-NONEXISTENT-999")
            self.assertEqual(resp.status_code, 404)
            data = resp.json()
            self.assertIn("detail", data)
            self.assertIn("code", data)
            self.assertIn("request_id", data)
            self.assertEqual(data["code"], "HTTP_404")

    async def test_02_request_id_propagation(self):
        """Test 2: Custom X-Request-ID is propagated in response headers."""
        custom_id = "req-custom-test-12345"
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.headers.get("X-Request-ID"), custom_id)

    async def test_03_health_readiness_behavior(self):
        """Test 3: /api/v1/health checks PostgreSQL & Redis availability."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/health")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["status"], "ok")
            self.assertIn("components", data)
            self.assertEqual(data["components"].get("postgres"), "healthy")
            self.assertIn(data["components"].get("redis"), ["healthy", "degraded"])

    async def test_04_idempotent_investigation_handling(self):
        """Test 4: Requesting investigation on an active run returns the existing run idempotently."""
        async with SessionLocal() as session:
            run1 = await start_investigation_run(session, "INC-2043")
            run2 = await start_investigation_run(session, "INC-2043")
            self.assertEqual(run1.id, run2.id)

    async def test_05_sensitive_values_masked_in_logs(self):
        """Test 5: Sensitive parameter keys (password, token, secret) are redacted in log formatter."""
        sanitized = sanitize_val("password", "super_secret_p@ssword")
        self.assertEqual(sanitized, "***REDACTED***")
        
        token_sanitized = sanitize_val("access_token", "jwt.payload.signature")
        self.assertEqual(token_sanitized, "***REDACTED***")
        
        normal_val = sanitize_val("service_id", "orders-service")
        self.assertEqual(normal_val, "orders-service")

    async def test_06_security_configuration(self):
        """Test 6: Security configuration contains valid settings and non-empty defaults."""
        settings = get_settings()
        self.assertIsNotNone(settings.secret_key)
        self.assertGreater(len(settings.secret_key), 10)
        self.assertIn("http://localhost:5173", settings.cors_origin_list)
