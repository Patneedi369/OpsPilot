from typing import Any, TypedDict

from app.schemas.investigation import InvestigationResult
from app.services.ai.context import InvestigationContext


class InvestigationGraphState(TypedDict, total=False):
    run_id: str
    incident_id: str
    thread_id: str
    context: InvestigationContext | None
    correlated_findings: list[dict[str, Any]]
    probable_root_cause: str
    confidence: int
    reasoning: str
    evidence: list[dict[str, str]]
    remediations: list[dict[str, Any]]
    result: InvestigationResult | None
    status: str
    current_step: str
    approval_decision: str | None
    approval_actor: str | None
    approval_note: str | None
    execution_summary: str | None
    error: str | None
