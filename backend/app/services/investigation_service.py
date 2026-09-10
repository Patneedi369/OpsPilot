from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deployment import Deployment
from app.models.incident import Incident
from app.models.incident_event import IncidentEvent
from app.models.log_entry import LogEntry
from app.repositories.incident_repository import incident_repository
from app.schemas.investigation import InvestigationResult
from app.services.ai.context import InvestigationContext
from app.services.ai.provider import get_investigator
from app.services.incidents import IncidentNotFoundError


def _event_dict(row: IncidentEvent) -> dict:
    return {
        "id": row.id,
        "incident_id": row.incident_id,
        "timestamp": row.timestamp,
        "title": row.title,
        "description": row.description,
        "type": row.type,
    }


def _log_dict(row: LogEntry) -> dict:
    return {
        "id": row.id,
        "incident_id": row.incident_id,
        "timestamp": row.timestamp,
        "level": row.level,
        "service": row.service,
        "message": row.message,
    }


def _deployment_dict(row: Deployment) -> dict:
    return {
        "id": row.id,
        "version": row.version,
        "service_id": row.service_id,
        "service_name": row.service_name,
        "author": row.author,
        "author_email": row.author_email,
        "deployed_at": row.deployed_at,
        "time_label": row.time_label,
        "status": row.status,
        "commit": row.commit,
        "commit_message": row.commit_message,
        "files_changed": row.files_changed,
    }


def build_context(
    incident: Incident,
    events: list[IncidentEvent],
    logs: list[LogEntry],
    deployments: list[Deployment],
) -> InvestigationContext:
    return InvestigationContext(
        incident_id=incident.id,
        title=incident.title,
        severity=incident.severity,
        status=incident.status,
        service_id=incident.service_id,
        service_name=incident.service_name,
        started_at=incident.started_at,
        trigger=incident.trigger,
        blast_radius=incident.blast_radius,
        affected_services=list(incident.affected_services or []),
        events=[_event_dict(item) for item in events],
        logs=[_log_dict(item) for item in logs],
        deployments=[_deployment_dict(item) for item in deployments],
    )


async def investigate_incident(session: AsyncSession, incident_id: str) -> InvestigationResult:
    incident = await incident_repository.get_by_id(session, incident_id)
    if incident is None:
        raise IncidentNotFoundError(incident_id)
    events = await incident_repository.list_events(session, incident_id)
    logs = await incident_repository.list_logs(session, incident_id)
    deployments = await incident_repository.list_deployments_for_service(session, incident.service_id)
    context = build_context(incident, events, logs, deployments)
    investigator = get_investigator()
    return await investigator.investigate(context)
