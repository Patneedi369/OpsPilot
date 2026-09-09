from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class ErrorResponse(BaseModel):
    detail: str


class AffectedService(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    service_id: str = Field(alias="serviceId")
    name: str
    health: Literal["ok", "warn", "crit"]
    metric: str


class Incident(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    title: str
    severity: Literal["SEV-1", "SEV-2", "SEV-3"]
    status: Literal[
        "detected",
        "investigating",
        "awaiting_approval",
        "executing",
        "verifying",
        "monitoring",
        "resolved",
    ]
    workflow_stage: Literal[
        "detection",
        "investigation",
        "evidence",
        "correlation",
        "root_cause",
        "remediation_proposal",
        "human_approval",
        "execution",
        "verification",
        "resolution",
    ] = Field(alias="workflowStage")
    service_id: str = Field(alias="serviceId")
    service_name: str = Field(alias="serviceName")
    started_at: str = Field(alias="startedAt")
    duration_label: str = Field(alias="durationLabel")
    elapsed_seconds: int = Field(alias="elapsedSeconds")
    trigger: str
    affected_services: list[AffectedService] = Field(alias="affectedServices")
    blast_radius: str = Field(alias="blastRadius")
