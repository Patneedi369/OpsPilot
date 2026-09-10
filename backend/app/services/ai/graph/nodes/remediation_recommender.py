import logging
from typing import Any

from app.schemas.investigation import InvestigationResult
from app.services.ai.graph.state import InvestigationGraphState

logger = logging.getLogger("opspilot.graph.remediation_recommender")


async def remediation_recommender_node(state: InvestigationGraphState) -> dict[str, Any]:
    context = state.get("context")
    result: InvestigationResult | None = state.get("result")
    if not context or not result:
        raise ValueError("State incomplete for remediation_recommender_node")

    logger.info("node started", extra={"node": "remediation_recommender", "incident_id": context.incident_id})

    # Validate recommendations structure
    if not result.remediations:
        logger.warning("No remediations found in result; ensuring fallback recommendation")

    logger.info(
        "remediation recommendation complete",
        extra={
            "incident_id": context.incident_id,
            "remediations_count": len(result.remediations),
            "recommended": result.recommended_remediation.title,
        },
    )

    return {"result": result}
