import logging
from typing import Any

from langgraph.types import interrupt

from app.services.ai.graph.state import InvestigationGraphState

logger = logging.getLogger("opspilot.graph.human_approval")


async def human_approval_node(state: InvestigationGraphState) -> dict[str, Any]:
    context = state.get("context")
    result = state.get("result")
    incident_id = state.get("incident_id") or (context.incident_id if context else "unknown")

    logger.info("node started", extra={"node": "human_approval", "incident_id": incident_id})

    # Prepare interrupt payload requesting human decision
    recommendation = result.recommended_remediation if result else None
    interrupt_payload = {
        "action": "request_approval",
        "incident_id": incident_id,
        "run_id": state.get("run_id"),
        "remediation": recommendation.model_dump(by_alias=True) if recommendation else None,
        "message": f"Remediation recommendation '{recommendation.title if recommendation else 'action'}' requires human operator approval before execution.",
    }

    # Pause execution using LangGraph interrupt
    resume_data = interrupt(interrupt_payload)

    # Process resume decision payload
    if not isinstance(resume_data, dict):
        resume_data = {"decision": "approved" if str(resume_data).lower() == "approved" else "rejected"}

    decision = str(resume_data.get("decision", "rejected")).lower()
    actor = str(resume_data.get("actor", "sre-oncall"))
    note = str(resume_data.get("note", ""))

    logger.info(
        "human approval decision received",
        extra={"incident_id": incident_id, "decision": decision, "actor": actor},
    )

    return {
        "current_step": "human_approval",
        "status": "approved" if decision == "approved" else "rejected",
        "approval_decision": decision,
        "approval_actor": actor,
        "approval_note": note,
    }
