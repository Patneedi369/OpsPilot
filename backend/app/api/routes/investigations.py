import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.incident import ErrorResponse
from app.schemas.investigation import (
    ApprovalRequest,
    InvestigationResult,
    InvestigationRunResponse,
    PendingApprovalResponse,
)
from app.services.incidents import IncidentNotFoundError
from app.services.investigation_service import (
    RunNotFoundError,
    approve_run,
    get_run,
    investigate_incident,
    list_runs,
    reject_run,
)

router = APIRouter()
logger = logging.getLogger("opspilot.api.investigations")


@router.post(
    "/{incident_id}/investigate",
    response_model=InvestigationResult,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
async def run_investigation(
    incident_id: str,
    session: AsyncSession = Depends(get_db),
) -> InvestigationResult:
    try:
        result = await investigate_incident(session, incident_id)
    except IncidentNotFoundError as exc:
        logger.info("investigation incident not found", extra={"incident_id": incident_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    logger.info(
        "investigation complete",
        extra={"incident_id": incident_id, "provider": result.provider, "confidence": result.confidence},
    )
    return result


@router.get(
    "/{incident_id}/runs",
    response_model=list[InvestigationRunResponse],
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
async def get_incident_runs(
    incident_id: str,
    session: AsyncSession = Depends(get_db),
) -> list[InvestigationRunResponse]:
    return await list_runs(session, incident_id)


@router.get(
    "/runs/{run_id}",
    response_model=InvestigationRunResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
async def get_investigation_run_by_id(
    run_id: str,
    session: AsyncSession = Depends(get_db),
) -> InvestigationRunResponse:
    try:
        return await get_run(session, run_id)
    except RunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/runs/{run_id}/approval",
    response_model=PendingApprovalResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
async def get_pending_approval(
    run_id: str,
    session: AsyncSession = Depends(get_db),
) -> PendingApprovalResponse:
    try:
        run = await get_run(session, run_id)
    except RunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    remediation = None
    if run.final_result and isinstance(run.final_result, dict):
        remediation = run.final_result.get("recommendedRemediation")

    return PendingApprovalResponse(
        runId=run.id,
        incidentId=run.incident_id,
        threadId=run.thread_id,
        status=run.status,
        recommendedRemediation=remediation,
        message=f"Investigation run {run.id} is {run.status}.",
    )


@router.post(
    "/runs/{run_id}/approve",
    response_model=InvestigationRunResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
async def approve_investigation_remediation(
    run_id: str,
    payload: ApprovalRequest = ApprovalRequest(),
    session: AsyncSession = Depends(get_db),
) -> InvestigationRunResponse:
    try:
        return await approve_run(
            session,
            run_id,
            actor=payload.actor,
            note=payload.note,
            simulate_execution_failure=payload.simulate_execution_failure,
            simulate_verification_failure=payload.simulate_verification_failure,
        )
    except RunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/runs/{run_id}/reject",
    response_model=InvestigationRunResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
async def reject_investigation_remediation(
    run_id: str,
    payload: ApprovalRequest = ApprovalRequest(),
    session: AsyncSession = Depends(get_db),
) -> InvestigationRunResponse:
    try:
        return await reject_run(session, run_id, actor=payload.actor, note=payload.note)
    except RunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
