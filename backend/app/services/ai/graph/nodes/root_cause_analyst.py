import logging
from typing import Any

from app.services.ai.graph.state import InvestigationGraphState
from app.services.ai.provider import get_investigator

logger = logging.getLogger("opspilot.graph.root_cause_analyst")


async def root_cause_analyst_node(state: InvestigationGraphState) -> dict[str, Any]:
    context = state.get("context")
    if not context:
        raise ValueError("Context missing in state for root_cause_analyst_node")

    logger.info("node started", extra={"node": "root_cause_analyst", "incident_id": context.incident_id})

    investigator = get_investigator()
    result = await investigator.investigate(context)

    logger.info(
        "root cause analysis complete",
        extra={
            "incident_id": context.incident_id,
            "provider": result.provider,
            "confidence": result.confidence,
        },
    )

    return {
        "probable_root_cause": result.probable_root_cause,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "evidence": [item.model_dump(by_alias=True) for item in result.evidence],
        "remediations": [item.model_dump(by_alias=True) for item in result.remediations],
        "result": result,
    }
