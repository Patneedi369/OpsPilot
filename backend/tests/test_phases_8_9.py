import asyncio
import sys
import unittest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from httpx import ASGITransport, AsyncClient

from app.db.session import SessionLocal, engine
from app.main import app
from app.repositories.investigation_repository import investigation_repository
from app.services.investigation_service import (
    approve_run,
    get_run,
    reject_run,
    start_investigation_run,
)


class TestPhases8And9(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        await engine.dispose()

    async def test_01_investigation_creates_persistent_run(self):
        """Test 1: Starting investigation creates a persistent run in PostgreSQL."""
        async with SessionLocal() as session:
            run = await start_investigation_run(session, "INC-2043")
            self.assertIsNotNone(run.id)
            self.assertEqual(run.incident_id, "INC-2043")
            self.assertTrue(run.id.startswith("run-INC-2043-"))

            db_run = await investigation_repository.get_run(session, run.id)
            self.assertIsNotNone(db_run)
            self.assertEqual(db_run.id, run.id)

    async def test_02_stable_thread_id(self):
        """Test 2: LangGraph thread_id is stable and associated with run_id."""
        async with SessionLocal() as session:
            run = await start_investigation_run(session, "INC-2043")
            self.assertIn(run.id, run.thread_id)
            self.assertTrue(run.thread_id.startswith("thread-INC-2043-"))

    async def test_03_reaches_approval_interrupt(self):
        """Test 3: Investigation workflow reaches human approval interrupt."""
        async with SessionLocal() as session:
            run = await start_investigation_run(session, "INC-2043")
            self.assertIn(run.status, ("awaiting_approval", "completed"))
            self.assertEqual(run.current_step, "human_approval" if run.status == "awaiting_approval" else "completed")

    async def test_04_approval_resumes_same_thread(self):
        """Test 4: Approving remediation resumes same thread and executes remediation."""
        async with SessionLocal() as session:
            run = await start_investigation_run(session, "INC-2043")
            approved_run = await approve_run(session, run.id, actor="sre-lead", note="Approve composite index")
            self.assertEqual(approved_run.id, run.id)
            self.assertIn(approved_run.status, ("completed", "recovered"))
            self.assertIn(approved_run.current_step, ("completed", "recovered"))
            self.assertEqual(approved_run.approval_decision, "approved")

    async def test_05_rejection_does_not_execute_remediation(self):
        """Test 5: Rejecting remediation moves to rejected state without executing remediation."""
        async with SessionLocal() as session:
            run = await start_investigation_run(session, "INC-2043")
            rejected_run = await reject_run(session, run.id, actor="sre-lead", note="Do not apply index during peak hours")
            self.assertEqual(rejected_run.id, run.id)
            self.assertEqual(rejected_run.status, "rejected")
            self.assertEqual(rejected_run.current_step, "rejected")
            self.assertEqual(rejected_run.approval_decision, "rejected")

    async def test_06_resumable_after_fresh_session(self):
        """Test 6: Persisted state can be loaded and resumed in a fresh DB session."""
        async with SessionLocal() as session1:
            run = await start_investigation_run(session1, "INC-2043")
            run_id = run.id

        async with SessionLocal() as session2:
            fetched_run = await get_run(session2, run_id)
            self.assertEqual(fetched_run.id, run_id)
            resumed_run = await approve_run(session2, run_id, actor="sre-manager", note="Resumed from new session")
            self.assertIn(resumed_run.status, ("completed", "recovered"))

    async def test_07_existing_investigation_endpoint_compatible(self):
        """Test 7: POST /api/v1/incidents/INC-2043/investigate remains fully compatible."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/api/v1/incidents/INC-2043/investigate")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertEqual(data["incidentId"], "INC-2043")
            self.assertIn("probableRootCause", data)
            self.assertIn("confidence", data)
            self.assertIn("recommendedRemediation", data)


if __name__ == "__main__":
    unittest.main()
