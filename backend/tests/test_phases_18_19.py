import asyncio
import sys
import unittest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from httpx import ASGITransport, AsyncClient

from app.persistence.session import SessionLocal, engine
from app.main import app
from app.schemas.investigation import EvidenceItem, InvestigationResult, RemediationOption, RootCause
from app.services.ai.context import InvestigationContext
from app.services.ai.evaluation import ai_evaluator
from app.services.ai.fallback import development_fallback
from app.services.ai.guardrails import guardrail_validator, scrub_secrets
from app.services.evidence_service import compute_evidence_score, evidence_service


class TestPhases18And19(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        await engine.dispose()

    async def test_01_temporal_and_causal_correlation_inc2043(self):
        """Test 1: Evidence chain preserves INC-2043 causal ordering and scoring."""
        ctx = InvestigationContext(
            incident_id="INC-2043",
            title="Unindexed order history query",
            severity="SEV-1",
            status="investigating",
            service_id="orders-service",
            service_name="Orders Service",
            started_at="2026-09-10T21:06:00Z",
            trigger="High latency & 5xx error rate",
            blast_radius="18% checkout sessions affected",
            events=[{"timestamp": "21:06:00Z", "type": "crit", "title": "5xx error rate spike", "description": "18.4% 5xx errors"}],
            logs=[{"timestamp": "21:04:30Z", "level": "ERROR", "service": "orders-service", "message": "Connection pool timeout after slow query"}],
            deployments=[{"version": "deploy-#4821", "service_id": "orders-service", "deployed_at": "21:04:12Z", "status": "deployed", "commit_message": "Unindexed order history query"}],
        )

        chain = evidence_service.build_evidence_chain(ctx)
        self.assertEqual(chain.incident_id, "INC-2043")
        self.assertGreaterEqual(len(chain.evidence), 2)
        self.assertIn("#4821", chain.causal_chain[0])
        self.assertGreaterEqual(chain.evidence[0].severity_relevance, 0.7)

    async def test_02_service_dependency_correlation_scoring(self):
        """Test 2: compute_evidence_score correctly weighs upstream service dependency relationships."""
        score_direct, reason_direct = compute_evidence_score(source="logs", service="orders-service", target_service="orders-service", is_critical=True)
        score_dep, reason_dep = compute_evidence_score(source="database", service="orders-db", target_service="orders-service", is_critical=True)
        
        self.assertGreaterEqual(score_direct, 0.8)
        self.assertGreaterEqual(score_dep, 0.7)
        self.assertIn("Direct match", reason_direct)
        self.assertIn("Upstream dependency", reason_dep)

    async def test_03_evidence_ranking_and_endpoint(self):
        """Test 3: GET /api/v1/incidents/{id}/evidence exposes sorted evidence chain."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/incidents/INC-2043/evidence")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["incidentId"], "INC-2043")
            self.assertIn("evidence", data)
            self.assertIn("causalChain", data)
            evidence = data["evidence"]
            if len(evidence) >= 2:
                self.assertGreaterEqual(evidence[0]["severityRelevance"], evidence[1]["severityRelevance"])

    async def test_04_ai_guardrails_confidence_and_secret_scrubbing(self):
        """Test 4: AIGuardrailValidator clamps out-of-bounds confidence and scrubs secrets."""
        ctx = InvestigationContext(
            incident_id="INC-TEST-GUARD",
            title="Guardrail test",
            severity="SEV-2",
            status="investigating",
            service_id="auth-service",
            service_name="Auth Service",
            started_at="2026-09-10T12:00:00Z",
            trigger="Secret test",
            blast_radius="Low",
        )

        raw_res = InvestigationResult(
            id="inv-guard",
            incident_id="INC-TEST-GUARD",
            status="complete",
            summary="Found secret Bearer eyJhbGciOiJIUzI1NiJ9.secretpayload.signature in output",
            probable_root_cause="Database credential secret_key_1234567890 leaked in log",
            evidence=[EvidenceItem(id="evd-1", source="logs", summary="Log entry")],
            affected_service="Auth Service",
            severity="SEV-2",
            confidence=150,  # Invalid confidence out of bounds (>100)
            recommended_remediation=RemediationOption(
                id="rem-test",
                title="Drop database production_db",  # Prohibited destructive action
                description="DROP DATABASE production_db to reset state",
                risk="high",
                eta_minutes=1,
                recommended=True,
                kind="infrastructure",
            ),
            investigated_at="2026-09-10T12:00:00Z",
            reasoning="Reasoning containing postgres://user:secretpass@host:5432/db",
            root_cause=RootCause(
                summary="Secret leak",
                confidence=150,
                expected_impact_if_unresolved="None",
                affected_users_estimate="None",
                model="test-model",
            ),
            remediations=[],
            model="test-model",
            provider="test-provider",
        )

        validated = guardrail_validator.validate_and_repair(raw_res, ctx)

        # 1. Confidence clamped to 100
        self.assertEqual(validated.confidence, 100)
        # 2. Secrets redacted
        self.assertNotIn("secretpass", validated.reasoning)
        self.assertIn("***REDACTED_SECRET***", validated.reasoning)
        # 3. Prohibited destructive action repaired
        self.assertNotIn("DROP DATABASE", validated.recommended_remediation.description)
        self.assertEqual(validated.recommended_remediation.title, "Safe Monitoring & Verification")
        # 4. Provider metadata populated
        self.assertIn("providerMetadata", validated.model_dump(by_alias=True))
        self.assertEqual(validated.provider_metadata["status"], "repaired")

    async def test_05_ai_evaluation_suite_provider_independent(self):
        """Test 5: AIEvaluationSuite runs 5 evaluation scenarios locally with 100% pass score."""
        eval_result = await ai_evaluator.run_evaluations()
        self.assertEqual(eval_result.total_scenarios, 5)
        self.assertEqual(eval_result.passed_scenarios, 5)
        self.assertEqual(eval_result.overall_score, 100.0)
        for res in eval_result.results:
            self.assertTrue(res.passed, f"Scenario {res.scenario_name} failed: {res.details}")
            self.assertTrue(res.root_cause_match)
            self.assertTrue(res.confidence_validity)
            self.assertTrue(res.remediation_safety)
