from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.incident_repository import incident_repository
from app.schemas.incident import Incident


class IncidentNotFoundError(Exception):
    def __init__(self, incident_id: str) -> None:
        self.incident_id = incident_id
        super().__init__(f"Incident {incident_id} not found")


def _normalize_service_item(item: object) -> dict:
    if isinstance(item, str):
        return {
            "serviceId": item,
            "name": item.replace("-", " ").title(),
            "health": "crit",
            "metric": "high_latency",
        }
    if isinstance(item, dict):
        return {
            "serviceId": item.get("serviceId") or item.get("service_id") or "unknown",
            "name": item.get("name") or item.get("serviceId") or "unknown",
            "health": item.get("health", "crit"),
            "metric": item.get("metric", "high_latency"),
        }
    return {"serviceId": "unknown", "name": "unknown", "health": "crit", "metric": "high_latency"}


def _to_schema(row: object) -> Incident:
    if hasattr(row, "affected_services") and isinstance(getattr(row, "affected_services"), list):
        row.affected_services = [_normalize_service_item(s) for s in getattr(row, "affected_services")]
    return Incident.model_validate(row, from_attributes=True)


async def list_incidents(session: AsyncSession) -> list[Incident]:
    rows = await incident_repository.list_all(session)
    return [_to_schema(row) for row in rows]


async def get_incident(session: AsyncSession, incident_id: str) -> Incident:
    row = await incident_repository.get_by_id(session, incident_id)
    if row is None:
        raise IncidentNotFoundError(incident_id)
    return _to_schema(row)
