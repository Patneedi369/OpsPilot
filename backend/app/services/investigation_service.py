import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investigation_run import InvestigationRun
from app.repositories.incident_repository import incident_repository
from app.repositories.investigation_repository import investigation_repository
from app.schemas.investigation import InvestigationResult
from app.services.ai.context import build_context
from app.services.ai.graph.workflow import get_graph_state, run_or_resume_graph
from app.services.incidents import IncidentNotFoundError

logger = logging.getLogger("opspilot.services.investigation")


class RunNotFoundError(Exception):
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        super().__init__(f"Investigation run {run_id} not found")


async def start_investigation_run(session: AsyncSession, incident_id: str) -> InvestigationRun:
    incident = await incident_repository.get_by_id(session, incident_id)
    if incident is None:
        raise IncidentNotFoundError(incident_id)

    # Idempotency check: return existing active run if present
    existing_runs = await investigation_repository.list_runs_for_incident(session, incident_id)
    active_run = next(
        (r for r in existing_runs if r.status in ["running", "awaiting_approval", "executing", "verifying_recovery"]),
        None,
    )
    if active_run:
        logger.info(
            "idempotent investigation request: active run found",
            extra={"incident_id": incident_id, "run_id": active_run.id, "status": active_run.status},
        )
        return active_run

    now_iso = datetime.now(timezone.utc).isoformat()
    run_uuid = uuid4().hex[:8]
    run_id = f"run-{incident_id}-{run_uuid}"
    thread_id = f"thread-{incident_id}-{run_id}"

    db_run = InvestigationRun(
        id=run_id,
        incident_id=incident_id,
        thread_id=thread_id,
        status="running",
        current_step="context_collection",
        started_at=now_iso,
    )
    await investigation_repository.create_run(session, db_run)

    initial_state = {
        "run_id": run_id,
        "incident_id": incident_id,
        "thread_id": thread_id,
    }

    try:
        final_state = await run_or_resume_graph(thread_id=thread_id, initial_state=initial_state)
        result: InvestigationResult | None = final_state.get("result")
        result_dict = result.model_dump(by_alias=True) if result else None

        # Check if interrupted at human approval
        graph_state = await get_graph_state(thread_id)
        if graph_state and graph_state.next:
            next_nodes = list(graph_state.next)
            if "human_approval" in next_nodes:
                updated_paused = await investigation_repository.update_run(
                    session,
                    run_id,
                    {
                        "status": "awaiting_approval",
                        "current_step": "human_approval",
                        "final_result": result_dict,
                    },
                )
                await incident_repository.update_status(
                    session,
                    incident_id=incident_id,
                    status="awaiting_approval",
                    workflow_stage="remediation_proposal",
                )
                logger.info("investigation run paused at human_approval interrupt", extra={"run_id": run_id})
                return updated_paused or db_run

        status = final_state.get("status", "completed")
        current_step = final_state.get("current_step", "completed")
        completed_at = datetime.now(timezone.utc).isoformat() if status in ("completed", "rejected", "recovered") else None

        updated = await investigation_repository.update_run(
            session,
            run_id,
            {
                "status": status,
                "current_step": current_step,
                "completed_at": completed_at,
                "final_result": result_dict,
                "execution_result": final_state.get("execution_result"),
                "verification_result": final_state.get("verification_result"),
            },
        )
        if status == "recovered":
            await incident_repository.update_status(
                session,
                incident_id=incident_id,
                status="resolved",
                workflow_stage="resolution",
            )
        return updated or db_run
    except Exception as exc:
        logger.exception("investigation run execution failed", extra={"run_id": run_id})
        await investigation_repository.update_run(
            session,
            run_id,
            {
                "status": "failed",
                "current_step": "failed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": str(exc),
            },
        )
        raise


async def get_run(session: AsyncSession, run_id: str) -> InvestigationRun:
    run = await investigation_repository.get_run(session, run_id)
    if run is None:
        raise RunNotFoundError(run_id)
    return run


async def list_runs(session: AsyncSession, incident_id: str) -> list[InvestigationRun]:
    return await investigation_repository.list_runs_for_incident(session, incident_id)


async def approve_run(
    session: AsyncSession,
    run_id: str,
    actor: str = "sre-lead",
    note: str = "Approved via OpsPilot workflow",
    simulate_execution_failure: bool = False,
    simulate_verification_failure: bool = False,
) -> InvestigationRun:
    run = await get_run(session, run_id)
    now_iso = datetime.now(timezone.utc).isoformat()

    await investigation_repository.update_run(
        session,
        run_id,
        {
            "status": "approved",
            "approval_decision": "approved",
            "approval_actor": actor,
            "approval_note": note,
            "approved_at": now_iso,
        },
    )

    resume_payload = {
        "decision": "approved",
        "actor": actor,
        "note": note,
        "simulate_execution_failure": simulate_execution_failure,
        "simulate_verification_failure": simulate_verification_failure,
    }
    final_state = await run_or_resume_graph(thread_id=run.thread_id, resume_payload=resume_payload)

    result: InvestigationResult | None = final_state.get("result")
    result_dict = result.model_dump(by_alias=True) if result else run.final_result
    status = final_state.get("status", "recovered")
    current_step = final_state.get("current_step", "recovered")

    updated = await investigation_repository.update_run(
        session,
        run_id,
        {
            "status": status,
            "current_step": current_step,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "final_result": result_dict,
            "execution_result": final_state.get("execution_result"),
            "verification_result": final_state.get("verification_result"),
            "error_message": final_state.get("error"),
        },
    )

    if status == "recovered":
        await incident_repository.update_status(
            session,
            incident_id=run.incident_id,
            status="resolved",
            workflow_stage="resolution",
        )
    elif status == "awaiting_approval":
        await incident_repository.update_status(
            session,
            incident_id=run.incident_id,
            status="awaiting_approval",
            workflow_stage="remediation_proposal",
        )
    elif status in ("executing", "verifying_recovery"):
        await incident_repository.update_status(
            session,
            incident_id=run.incident_id,
            status="executing" if status == "executing" else "verifying",
            workflow_stage="execution" if status == "executing" else "verification",
        )

    return updated or run


async def reject_run(session: AsyncSession, run_id: str, actor: str = "sre-lead", note: str = "Rejected proposal") -> InvestigationRun:
    run = await get_run(session, run_id)
    now_iso = datetime.now(timezone.utc).isoformat()

    await investigation_repository.update_run(
        session,
        run_id,
        {
            "status": "rejected",
            "approval_decision": "rejected",
            "approval_actor": actor,
            "approval_note": note,
            "approved_at": now_iso,
        },
    )

    resume_payload = {"decision": "rejected", "actor": actor, "note": note}
    final_state = await run_or_resume_graph(thread_id=run.thread_id, resume_payload=resume_payload)

    result: InvestigationResult | None = final_state.get("result")
    result_dict = result.model_dump(by_alias=True) if result else run.final_result

    updated = await investigation_repository.update_run(
        session,
        run_id,
        {
            "status": "rejected",
            "current_step": "rejected",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "final_result": result_dict,
            "execution_result": final_state.get("execution_result"),
            "verification_result": final_state.get("verification_result"),
        },
    )
    await incident_repository.update_status(
        session,
        incident_id=run.incident_id,
        status="monitoring",
        workflow_stage="investigation",
    )
    return updated or run



async def investigate_incident(session: AsyncSession, incident_id: str) -> InvestigationResult:
    latest_run = await investigation_repository.get_latest_run_for_incident(session, incident_id)
    if latest_run is None or latest_run.status in ("failed",):
        latest_run = await start_investigation_run(session, incident_id)

    if latest_run.final_result:
        return InvestigationResult.model_validate(latest_run.final_result)

    events = await incident_repository.list_events(session, incident_id)
    logs = await incident_repository.list_logs(session, incident_id)
    incident = await incident_repository.get_by_id(session, incident_id)
    if incident is None:
        raise IncidentNotFoundError(incident_id)
    deployments = await incident_repository.list_deployments_for_service(session, incident.service_id)
    context = build_context(incident, events, logs, deployments)
    from app.services.ai.provider import get_investigator
    return await get_investigator().investigate(context)
