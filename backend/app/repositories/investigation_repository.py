import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investigation_run import InvestigationRun

logger = logging.getLogger("opspilot.repositories.investigation")


class InvestigationRepository:
    async def create_run(self, session: AsyncSession, run: InvestigationRun) -> InvestigationRun:
        session.add(run)
        await session.commit()
        await session.refresh(run)
        return run

    async def get_run(self, session: AsyncSession, run_id: str) -> InvestigationRun | None:
        return await session.get(InvestigationRun, run_id)

    async def get_latest_run_for_incident(self, session: AsyncSession, incident_id: str) -> InvestigationRun | None:
        result = await session.execute(
            select(InvestigationRun)
            .where(InvestigationRun.incident_id == incident_id)
            .order_by(InvestigationRun.started_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def list_runs_for_incident(self, session: AsyncSession, incident_id: str) -> list[InvestigationRun]:
        result = await session.execute(
            select(InvestigationRun)
            .where(InvestigationRun.incident_id == incident_id)
            .order_by(InvestigationRun.started_at.desc())
        )
        return list(result.scalars().all())

    async def update_run(self, session: AsyncSession, run_id: str, updates: dict[str, Any]) -> InvestigationRun | None:
        run = await session.get(InvestigationRun, run_id)
        if run is None:
            return None
        for key, value in updates.items():
            if hasattr(run, key):
                setattr(run, key, value)
        await session.commit()
        await session.refresh(run)
        return run


investigation_repository = InvestigationRepository()
