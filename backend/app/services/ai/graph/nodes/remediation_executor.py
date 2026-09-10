import logging
from typing import Any

from app.services.ai.graph.state import InvestigationGraphState

logger = logging.getLogger("opspilot.graph.remediation_executor")


async def remediation_executor_node(state: InvestigationGraphState) -> dict[str, Any]:
    context = state.get("context")
    result = state.get("result")
    incident_id = state.get("incident_id") or (context.incident_id if context else "unknown")

    logger.info("node started - executing approved remediation", extra={"node": "remediation_executor", "incident_id": incident_id})

    recommendation_title = result.recommended_remediation.title if result and result.recommended_remediation else "Recommended remediation"
    
    # Safe mock remediation execution abstraction
    execution_summary = (
        f"Remediation '{recommendation_title}' executed safely: "
        f"applied index optimization on {context.service_name if context else 'service'} "
        f"and adjusted connection pool ceiling."
    )

    logger.info(
        "remediation execution complete",
        extra={"incident_id": incident_id, "summary": execution_summary},
    )

    return {
        "current_step": "completed",
        "status": "completed",
        "execution_summary": execution_summary,
    }
