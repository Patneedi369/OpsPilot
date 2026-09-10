from dataclasses import dataclass, field
from typing import Any

from app.models.deployment import Deployment
from app.models.incident import Incident
from app.models.incident_event import IncidentEvent
from app.models.log_entry import LogEntry


@dataclass
class InvestigationContext:
    incident_id: str
    title: str
    severity: str
    status: str
    service_id: str
    service_name: str
    started_at: str
    trigger: str
    blast_radius: str
    affected_services: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    logs: list[dict[str, Any]] = field(default_factory=list)
    deployments: list[dict[str, Any]] = field(default_factory=list)

    def to_prompt_block(self) -> str:
        lines = [
            f"INCIDENT: {self.incident_id} — {self.title}",
            f"SEVERITY: {self.severity}",
            f"STATUS: {self.status}",
            f"SERVICE: {self.service_name} ({self.service_id})",
            f"STARTED: {self.started_at}",
            f"TRIGGER: {self.trigger}",
            f"BLAST RADIUS: {self.blast_radius}",
            "AFFECTED SERVICES:",
        ]
        for item in self.affected_services:
            lines.append(f"- {item}")
        lines.append("TIMELINE EVENTS:")
        for event in self.events:
            lines.append(
                f"- [{event.get('timestamp')}] ({event.get('type')}) {event.get('title')}: {event.get('description')}"
            )
        lines.append("DEPLOYMENTS:")
        for deployment in self.deployments:
            lines.append(
                f"- {deployment.get('version')} {deployment.get('service_name')} "
                f"{deployment.get('deployed_at')} commit={deployment.get('commit')} "
                f"{deployment.get('commit_message')} status={deployment.get('status')}"
            )
        lines.append("LOGS:")
        for log in self.logs:
            lines.append(
                f"- {log.get('timestamp')} {log.get('level')} [{log.get('service')}] {log.get('message')}"
            )
        return "\n".join(lines)


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
