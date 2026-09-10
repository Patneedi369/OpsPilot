import logging
from typing import Any

from app.services.ai.graph.state import InvestigationGraphState
from app.services.verification_service import verification_service

logger = logging.getLogger("opspilot.graph.recovery_verifier")


async def recovery_verifier_node(state: InvestigationGraphState) -> dict[str, Any]:
    context = state.get("context")
    incident_id = state.get("incident_id") or (context.incident_id if context else "unknown")
    simulate_failure = bool(state.get("simulate_verification_failure"))

    logger.info("node started - verifying incident recovery", extra={"node": "recovery_verifier", "incident_id": incident_id})

    from app.core.events import event_bus
    event_bus.publish(incident_id=incident_id, event_type="recovery_verification_started", payload={}, status="verifying_recovery")

    ver_res = await verification_service.verify_recovery(
        incident_id=incident_id,
        simulate_failure=simulate_failure,
    )

    ver_dict = ver_res.to_dict()

    if ver_res.status == "verification_failed":
        logger.warning(
            "recovery verification failed",
            extra={"incident_id": incident_id, "error": ver_res.error},
        )
        event_bus.publish(incident_id=incident_id, event_type="recovery_verification_failed", payload=ver_dict, status="verification_failed")
        return {
            "current_step": "verification_failed",
            "status": "verification_failed",
            "verification_result": ver_dict,
            "error": ver_res.error,
        }

    logger.info(
        "recovery verification succeeded - incident recovered",
        extra={"incident_id": incident_id, "signals": len(ver_res.signals_checked)},
    )

    event_bus.publish(incident_id=incident_id, event_type="incident_recovered", payload=ver_dict, status="recovered")

    return {
        "current_step": "recovered",
        "status": "recovered",
        "verification_result": ver_dict,
    }
