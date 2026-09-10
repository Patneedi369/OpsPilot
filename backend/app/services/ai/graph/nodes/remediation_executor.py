import logging
from typing import Any

from app.services.ai.graph.state import InvestigationGraphState
from app.services.remediation_service import remediation_service

logger = logging.getLogger("opspilot.graph.remediation_executor")


async def remediation_executor_node(state: InvestigationGraphState) -> dict[str, Any]:
    context = state.get("context")
    result = state.get("result")
    incident_id = state.get("incident_id") or (context.incident_id if context else "unknown")
    simulate_failure = bool(state.get("simulate_execution_failure"))

    logger.info("node started - executing approved remediation", extra={"node": "remediation_executor", "incident_id": incident_id})

    remediation_dict = result.recommended_remediation.model_dump(by_alias=True) if result and result.recommended_remediation else None

    exec_res = await remediation_service.execute_remediation(
        incident_id=incident_id,
        remediation=remediation_dict,
        simulate_failure=simulate_failure,
    )

    exec_dict = exec_res.to_dict()

    if exec_res.status == "failed":
        logger.error(
            "remediation execution failed; halting before verification",
            extra={"incident_id": incident_id, "error": exec_res.error},
        )
        return {
            "current_step": "remediation_failed",
            "status": "remediation_failed",
            "execution_summary": exec_res.details,
            "execution_result": exec_dict,
            "error": exec_res.error,
        }

    logger.info(
        "remediation execution succeeded; advancing to recovery verification",
        extra={"incident_id": incident_id, "summary": exec_res.details},
    )

    return {
        "current_step": "verifying_recovery",
        "status": "executing",
        "execution_summary": exec_res.details,
        "execution_result": exec_dict,
    }
