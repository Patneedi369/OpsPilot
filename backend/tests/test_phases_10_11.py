import asyncio
import sys
import unittest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.db.session import SessionLocal, engine
from app.repositories.investigation_repository import investigation_repository
from app.services.investigation_service import (
    approve_run,
    get_run,
    reject_run,
    start_investigation_run,
)
from app.services.remediation_service import remediation_service
from app.services.verification_service import verification_service


class TestPhases10And11(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        await engine.dispose()

    async def test_01_approved_remediation_executes_and_recovers(self):
        """Test 1: Approved remediation executes and proceeds to recovery verification -> recovered."""
        async with SessionLocal() as session:
            run = await start_investigation_run(session, "INC-2043")
            approved_run = await approve_run(session, run.id, actor="sre-lead", note="Approve composite index")
            self.assertEqual(approved_run.id, run.id)
            self.assertEqual(approved_run.status, "recovered")
            self.assertEqual(approved_run.current_step, "recovered")
            self.assertIsNotNone(approved_run.execution_result)
            self.assertEqual(approved_run.execution_result["status"], "succeeded")
            self.assertIsNotNone(approved_run.verification_result)
            self.assertEqual(approved_run.verification_result["status"], "recovered")

    async def test_02_rejected_remediation_does_not_execute(self):
        """Test 2: Rejected remediation stops at rejected state without executing remediation."""
        async with SessionLocal() as session:
            run = await start_investigation_run(session, "INC-2043")
            rejected_run = await reject_run(session, run.id, actor="sre-lead", note="Reject remediation")
            self.assertEqual(rejected_run.status, "rejected")
            self.assertEqual(rejected_run.current_step, "rejected")
            self.assertIsNone(rejected_run.execution_result)
            self.assertIsNone(rejected_run.verification_result)

    async def test_03_remediation_failure_produces_remediation_failed(self):
        """Test 3: Remediation execution failure produces remediation_failed and skips verification."""
        async with SessionLocal() as session:
            run = await start_investigation_run(session, "INC-2043")
            failed_run = await approve_run(
                session,
                run.id,
                actor="sre-lead",
                note="Approve with execution error simulation",
                simulate_execution_failure=True,
            )
            self.assertEqual(failed_run.status, "remediation_failed")
            self.assertEqual(failed_run.current_step, "remediation_failed")
            self.assertIsNotNone(failed_run.execution_result)
            self.assertEqual(failed_run.execution_result["status"], "failed")
            self.assertIsNone(failed_run.verification_result)

    async def test_04_successful_remediation_proceeds_to_verification(self):
        """Test 4: Successful remediation execution moves to verifying_recovery stage."""
        exec_res = await remediation_service.execute_remediation("INC-2043", simulate_failure=False)
        self.assertEqual(exec_res.status, "succeeded")
        self.assertGreater(len(exec_res.actions_performed), 0)

    async def test_05_recovery_verification_succeeds(self):
        """Test 5: Multi-signal recovery verification passes when thresholds are satisfied."""
        ver_res = await verification_service.verify_recovery("INC-2043", simulate_failure=False)
        self.assertEqual(ver_res.status, "recovered")
        self.assertEqual(len(ver_res.signals_checked), 4)
        for sig in ver_res.signals_checked:
            self.assertEqual(sig["status"], "PASS")

    async def test_06_recovery_verification_failure_produces_verification_failed(self):
        """Test 6: Recovery verification failure produces verification_failed state."""
        async with SessionLocal() as session:
            run = await start_investigation_run(session, "INC-2043")
            failed_ver_run = await approve_run(
                session,
                run.id,
                actor="sre-lead",
                note="Approve with verification failure simulation",
                simulate_verification_failure=True,
            )
            self.assertEqual(failed_ver_run.status, "verification_failed")
            self.assertEqual(failed_ver_run.current_step, "verification_failed")
            self.assertIsNotNone(failed_ver_run.execution_result)
            self.assertEqual(failed_ver_run.execution_result["status"], "succeeded")
            self.assertIsNotNone(failed_ver_run.verification_result)
            self.assertEqual(failed_ver_run.verification_result["status"], "verification_failed")

    async def test_07_checkpoint_resume_survives_fresh_session(self):
        """Test 7: Execution & verification state survives checkpoint and fresh DB session."""
        async with SessionLocal() as session1:
            run = await start_investigation_run(session1, "INC-2043")
            run_id = run.id

        async with SessionLocal() as session2:
            resumed_run = await approve_run(session2, run_id, actor="sre-manager", note="Approved in fresh session")
            self.assertEqual(resumed_run.status, "recovered")
            self.assertEqual(resumed_run.execution_result["status"], "succeeded")
            self.assertEqual(resumed_run.verification_result["status"], "recovered")


if __name__ == "__main__":
    unittest.main()
