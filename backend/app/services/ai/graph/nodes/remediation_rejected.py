import logging
from typing import Any

from app.services.ai.graph.state import InvestigationGraphState

logger = logging.getLogger("opspilot.graph.remediation_rejected")


async def remediation_rejected_node(state: InvestigationGraphState) -> dict[str, Any]:
    context = state.get("context")
    incident_id = state.get("incident_id") or (context.incident_id if context else "unknown")
    note = state.get("approval_note") or "Operator rejected proposal"

    logger.info("node started - remediation rejected", extra={"node": "remediation_rejected", "incident_id": incident_id})

    execution_summary = f"Remediation was rejected by operator: '{note}'. No system changes were executed."

    logger.info(
        "remediation rejection finalized",
        extra={"incident_id": incident_id, "summary": execution_summary},
    )

    return {
        "current_step": "rejected",
        "status": "rejected",
        "execution_summary": execution_summary,
    }
