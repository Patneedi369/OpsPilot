import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.incident import ErrorResponse
from app.schemas.investigation import InvestigationResult
from app.services.incidents import IncidentNotFoundError
from app.services.investigation_service import investigate_incident

router = APIRouter()
logger = logging.getLogger(__name__)


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
