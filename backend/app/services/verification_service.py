import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("opspilot.services.verification")


@dataclass
class RecoveryVerificationResult:
    verified_at: str
    status: str  # "recovered" | "verification_failed"
    signals_checked: list[dict[str, Any]] = field(default_factory=list)
    details: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "verified_at": self.verified_at,
            "status": self.status,
            "signals_checked": self.signals_checked,
            "details": self.details,
            "error": self.error,
        }


class VerificationService:
    async def verify_recovery(
        self,
        incident_id: str,
        simulate_failure: bool = False,
    ) -> RecoveryVerificationResult:
        verified_at = datetime.now(timezone.utc).isoformat()
        logger.info(
            "starting recovery verification",
            extra={"incident_id": incident_id, "simulate_failure": simulate_failure},
        )

        if simulate_failure:
            signals_failed = [
                {
                    "metric": "p95_latency_ms",
                    "observed": 4820,
                    "threshold": 300,
                    "unit": "ms",
                    "status": "FAIL",
                },
                {
                    "metric": "http_5xx_error_rate_pct",
                    "observed": 18.4,
                    "threshold": 1.0,
                    "unit": "%",
                    "status": "FAIL",
                },
                {
                    "metric": "db_pool_utilization_pct",
                    "observed": 91.0,
                    "threshold": 60.0,
                    "unit": "%",
                    "status": "FAIL",
                },
            ]
            error_msg = "Verification failed: API p95 latency (4820ms) and 5xx error rate (18.4%) remain above healthy threshold."
            logger.warning("recovery verification failed", extra={"incident_id": incident_id, "error": error_msg})
            return RecoveryVerificationResult(
                verified_at=verified_at,
                status="verification_failed",
                signals_checked=signals_failed,
                details="Post-remediation signals demonstrate ongoing performance degradation.",
                error=error_msg,
            )

        # Successful verification signals for INC-2043
        signals_passed = [
            {
                "metric": "p95_latency_ms",
                "observed": 245,
                "threshold": 300,
                "unit": "ms",
                "status": "PASS",
            },
            {
                "metric": "http_5xx_error_rate_pct",
                "observed": 0.12,
                "threshold": 1.0,
                "unit": "%",
                "status": "PASS",
            },
            {
                "metric": "db_pool_utilization_pct",
                "observed": 42.0,
                "threshold": 60.0,
                "unit": "%",
                "status": "PASS",
            },
            {
                "metric": "avg_query_time_ms",
                "observed": 38,
                "threshold": 50,
                "unit": "ms",
                "status": "PASS",
            },
        ]
        details = (
            f"All 4 telemetry signals passed recovery thresholds. "
            f"API p95 latency normalized to 245ms, HTTP 5xx errors fell to 0.12%, "
            f"and DB pool utilization stabilized at 42%."
        )

        logger.info("recovery verification succeeded", extra={"incident_id": incident_id, "signals_count": len(signals_passed)})
        return RecoveryVerificationResult(
            verified_at=verified_at,
            status="recovered",
            signals_checked=signals_passed,
            details=details,
            error=None,
        )


verification_service = VerificationService()
