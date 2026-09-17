import logging
from typing import Any

from app.persistence.session import SessionLocal
from app.repositories.incident_repository import incident_repository
from app.services.ai.context import build_context
from app.services.ai.graph.state import InvestigationGraphState
from app.services.incidents import IncidentNotFoundError

logger = logging.getLogger("opspilot.graph.context_collector")


async def context_collector_node(state: InvestigationGraphState) -> dict[str, Any]:
    incident_id = state["incident_id"]

    logger.info("node started", extra={"node": "context_collector", "incident_id": incident_id})
    async with SessionLocal() as session:
        incident = await incident_repository.get_by_id(session, incident_id)
        if incident is None:
            raise IncidentNotFoundError(incident_id)

        events = await incident_repository.list_events(session, incident_id)
        logs = await incident_repository.list_logs(session, incident_id)
        deployments = await incident_repository.list_deployments_for_service(session, incident.service_id)

        context = build_context(incident, events, logs, deployments)

    logger.info(
        "context collected",
        extra={
            "incident_id": incident_id,
            "events_count": len(events),
            "logs_count": len(logs),
            "deployments_count": len(deployments),
        },
    )
    return {"context": context}
