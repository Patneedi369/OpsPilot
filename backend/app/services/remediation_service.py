import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("opspilot.services.remediation")


@dataclass
class RemediationExecutionResult:
    started_at: str
    completed_at: str
    status: str  # "succeeded" | "failed"
    actions_performed: list[dict[str, str]] = field(default_factory=list)
    details: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "actions_performed": self.actions_performed,
            "details": self.details,
            "error": self.error,
        }


class RemediationService:
    async def execute_remediation(
        self,
        incident_id: str,
        remediation: dict[str, Any] | None = None,
        simulate_failure: bool = False,
    ) -> RemediationExecutionResult:
        started_at = datetime.now(timezone.utc).isoformat()
        logger.info(
            "starting remediation execution",
            extra={"incident_id": incident_id, "simulate_failure": simulate_failure},
        )

        title = remediation.get("title") if remediation else "Remediation"
        should_fail = simulate_failure or bool(remediation and remediation.get("simulate_failure"))

        if should_fail:
            completed_at = datetime.now(timezone.utc).isoformat()
            error_msg = f"Remediation '{title}' failed: DDL lock timeout while applying composite index."
            logger.error("remediation execution failed", extra={"incident_id": incident_id, "error": error_msg})
            return RemediationExecutionResult(
                started_at=started_at,
                completed_at=completed_at,
                status="failed",
                actions_performed=[
                    {
                        "action": "CREATE INDEX CONCURRENTLY idx_orders_customer_created ON orders (customer_id, created_at)",
                        "status": "failed",
                    }
                ],
                details=f"Execution halted due to DDL lock acquisition timeout on orders table.",
                error=error_msg,
            )

        # Successful simulation path for INC-2043
        actions = [
            {
                "action": "CREATE INDEX CONCURRENTLY idx_orders_customer_created ON orders (customer_id, created_at);",
                "status": "succeeded",
                "duration_ms": "420",
            },
            {
                "action": "ALTER SYSTEM SET max_connections = '300'; SELECT pg_reload_conf();",
                "status": "succeeded",
                "duration_ms": "15",
            },
        ]
        completed_at = datetime.now(timezone.utc).isoformat()
        details = (
            f"Successfully created composite index on orders(customer_id, created_at) "
            f"and expanded connection pool ceiling to 300 connections."
        )

        logger.info("remediation execution succeeded", extra={"incident_id": incident_id, "actions_count": len(actions)})
        return RemediationExecutionResult(
            started_at=started_at,
            completed_at=completed_at,
            status="succeeded",
            actions_performed=actions,
            details=details,
            error=None,
        )


remediation_service = RemediationService()
