from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident


class IncidentRepository:
    async def list_all(self, session: AsyncSession) -> list[Incident]:
        result = await session.execute(select(Incident).order_by(Incident.id.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, session: AsyncSession, incident_id: str) -> Incident | None:
        return await session.get(Incident, incident_id)


incident_repository = IncidentRepository()
