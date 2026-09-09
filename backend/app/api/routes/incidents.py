import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.incident import ErrorResponse, Incident
from app.services.incidents import IncidentNotFoundError, get_incident, list_incidents

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=list[Incident])
def get_incidents() -> list[Incident]:
    incidents = list_incidents()
    logger.info("listed incidents", extra={"count": len(incidents)})
    return incidents


@router.get(
    "/{incident_id}",
    response_model=Incident,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
def get_incident_by_id(incident_id: str) -> Incident:
    try:
        incident = get_incident(incident_id)
    except IncidentNotFoundError as exc:
        logger.info("incident not found", extra={"incident_id": incident_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return incident
