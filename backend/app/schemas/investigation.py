from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    source: Literal["metrics", "logs", "deployment", "database", "topology"]
    summary: str


class RemediationOption(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    title: str
    description: str
    risk: Literal["low", "medium", "high"]
    eta_minutes: int = Field(alias="etaMinutes")
    recommended: bool
    kind: Literal["rollback", "infrastructure", "forward_fix"]


class RootCause(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    summary: str
    confidence: int
    expected_impact_if_unresolved: str = Field(alias="expectedImpactIfUnresolved")
    affected_users_estimate: str = Field(alias="affectedUsersEstimate")
    model: str


class InvestigationResult(BaseModel):
    """API payload consumed by the OpsPilot frontend investigation panel."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    incident_id: str = Field(alias="incidentId")
    status: Literal["complete"]
    summary: str
    probable_root_cause: str = Field(alias="probableRootCause")
    evidence: list[EvidenceItem]
    affected_service: str = Field(alias="affectedService")
    severity: str
    confidence: int
    recommended_remediation: RemediationOption = Field(alias="recommendedRemediation")
    investigated_at: str = Field(alias="investigatedAt")
    reasoning: str
    root_cause: RootCause = Field(alias="rootCause")
    remediations: list[RemediationOption]
    model: str
    provider: str
