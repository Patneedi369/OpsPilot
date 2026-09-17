import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.incident_repository import incident_repository
from app.repositories.investigation_repository import investigation_repository
from app.schemas.evidence import EvidenceChainResponse
from app.schemas.incident import ErrorResponse
from app.services.ai.context import build_context
from app.services.evidence_service import evidence_service

router = APIRouter()
logger = logging.getLogger("opspilot.api.evidence")


@router.get(
    "/{incident_id}/evidence",
    response_model=EvidenceChainResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
async def get_incident_evidence_chain(
    incident_id: str,
    session: AsyncSession = Depends(get_db),
) -> EvidenceChainResponse:
    incident = await incident_repository.get_by_id(session, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )

    events = await incident_repository.list_events(session, incident_id)
    logs = await incident_repository.list_logs(session, incident_id)
    deployments = await incident_repository.list_deployments(session, incident.service_id)

    context = build_context(incident, events, logs, deployments)
    chain = evidence_service.build_evidence_chain(context)
    return chain
