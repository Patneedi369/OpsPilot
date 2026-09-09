from app.schemas.incident import Incident
from app.services.incident_catalog import INCIDENTS


class IncidentNotFoundError(Exception):
    def __init__(self, incident_id: str) -> None:
        self.incident_id = incident_id
        super().__init__(f"Incident {incident_id} not found")


def list_incidents() -> list[Incident]:
    return list(INCIDENTS)


def get_incident(incident_id: str) -> Incident:
    for incident in INCIDENTS:
        if incident.id == incident_id:
            return incident
    raise IncidentNotFoundError(incident_id)
