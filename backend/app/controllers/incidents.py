import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.incident import ErrorResponse, Incident
from app.services.incidents import IncidentNotFoundError, get_incident, list_incidents

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=list[Incident])
async def get_incidents(session: AsyncSession = Depends(get_db)) -> list[Incident]:
    incidents = await list_incidents(session)
    logger.info("listed incidents", extra={"count": len(incidents), "source": "postgres"})
    return incidents


@router.get(
    "/{incident_id}",
    response_model=Incident,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
async def get_incident_by_id(
    incident_id: str,
    session: AsyncSession = Depends(get_db),
) -> Incident:
    try:
        incident = await get_incident(session, incident_id)
    except IncidentNotFoundError as exc:
        logger.info("incident not found", extra={"incident_id": incident_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return incident
