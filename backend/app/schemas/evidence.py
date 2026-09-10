from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class NormalizedEvidence(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    evidence_id: str = Field(alias="evidenceId")
    source: Literal["metrics", "logs", "deployment", "database", "topology"]
    timestamp: str
    signal_type: str = Field(alias="signalType")
    service: str
    severity_relevance: float = Field(alias="severityRelevance")
    summary: str
    correlation_reason: str = Field(alias="correlationReason")
    raw_data: dict[str, Any] | None = Field(default=None, alias="rawData")


class EvidenceChainResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    incident_id: str = Field(alias="incidentId")
    total_evidence_count: int = Field(alias="totalEvidenceCount")
    causal_chain: list[str] = Field(alias="causalChain")
    evidence: list[NormalizedEvidence]
