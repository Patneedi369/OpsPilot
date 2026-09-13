# pyrefly: ignore [missing-import]
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deployment import Deployment
from app.models.incident import Incident
from app.models.incident_event import IncidentEvent
from app.models.log_entry import LogEntry


class IncidentRepository:
    async def list_all(self, session: AsyncSession) -> list[Incident]:
        result = await session.execute(select(Incident).order_by(Incident.id.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, session: AsyncSession, incident_id: str) -> Incident | None:
        return await session.get(Incident, incident_id)

    async def list_events(self, session: AsyncSession, incident_id: str) -> list[IncidentEvent]:
        result = await session.execute(
            select(IncidentEvent)
            .where(IncidentEvent.incident_id == incident_id)
            .order_by(IncidentEvent.timestamp.asc())
        )
        return list(result.scalars().all())

    async def list_logs(self, session: AsyncSession, incident_id: str) -> list[LogEntry]:
        result = await session.execute(
            select(LogEntry).where(LogEntry.incident_id == incident_id).order_by(LogEntry.timestamp.asc())
        )
        return list(result.scalars().all())

    async def list_deployments_for_service(self, session: AsyncSession, service_id: str) -> list[Deployment]:
        result = await session.execute(
            select(Deployment).where(Deployment.service_id == service_id).order_by(Deployment.time_label.desc())
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        session: AsyncSession,
        incident_id: str,
        status: str,
        workflow_stage: str | None = None,
    ) -> Incident | None:
        incident = await session.get(Incident, incident_id)
        if incident is None:
            return None
        incident.status = status
        if workflow_stage:
            incident.workflow_stage = workflow_stage
        await session.commit()
        await session.refresh(incident)
        return incident


incident_repository = IncidentRepository()
