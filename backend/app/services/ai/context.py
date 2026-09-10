from dataclasses import dataclass, field
from typing import Any


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
