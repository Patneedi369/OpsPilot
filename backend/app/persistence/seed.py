import asyncio
import logging

from sqlalchemy import delete, func, select

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.seed_data import DEPLOYMENTS, EVENTS, LOGS, incident_rows
from app.db.session import SessionLocal, engine
from app.models.deployment import Deployment
from app.models.incident import Incident
from app.models.incident_event import IncidentEvent
from app.models.log_entry import LogEntry

logger = logging.getLogger("opspilot.seed")


def _incident_orm(schema: object) -> Incident:
    payload = schema.model_dump(by_alias=True)
    return Incident(
        id=payload["id"],
        title=payload["title"],
        severity=payload["severity"],
        status=payload["status"],
        workflow_stage=payload["workflowStage"],
        service_id=payload["serviceId"],
        service_name=payload["serviceName"],
        started_at=payload["startedAt"],
        duration_label=payload["durationLabel"],
        elapsed_seconds=payload["elapsedSeconds"],
        trigger=payload["trigger"],
        affected_services=payload["affectedServices"],
        blast_radius=payload["blastRadius"],
    )


async def seed() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    async with SessionLocal() as session:
        existing = await session.scalar(select(func.count()).select_from(Incident))
        await session.execute(delete(LogEntry))
        await session.execute(delete(IncidentEvent))
        await session.execute(delete(Deployment))
        await session.execute(delete(Incident))

        for row in incident_rows():
            session.add(_incident_orm(row))
        for event in EVENTS:
            session.add(IncidentEvent(**event))
        for log in LOGS:
            session.add(LogEntry(**log))
        for deployment in DEPLOYMENTS:
            session.add(Deployment(**deployment))
        await session.commit()
        logger.info(
            "seed complete",
            extra={
                "replaced_existing": bool(existing),
                "incidents": len(incident_rows()),
                "events": len(EVENTS),
                "logs": len(LOGS),
                "deployments": len(DEPLOYMENTS),
            },
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
