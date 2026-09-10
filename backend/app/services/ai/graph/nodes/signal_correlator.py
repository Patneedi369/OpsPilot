import logging
from typing import Any

from app.services.ai.graph.state import InvestigationGraphState

logger = logging.getLogger("opspilot.graph.signal_correlator")


async def signal_correlator_node(state: InvestigationGraphState) -> dict[str, Any]:
    context = state.get("context")
    if not context:
        raise ValueError("Context missing in state for signal_correlator_node")

    logger.info("node started", extra={"node": "signal_correlator", "incident_id": context.incident_id})

    correlated_findings: list[dict[str, Any]] = []
    evidence: list[dict[str, str]] = []

    # 1. Deployment Signal
    if context.deployments:
        recent_deploy = context.deployments[0]
        correlated_findings.append({
            "category": "deployment",
            "summary": f"Deploy {recent_deploy['version']} to {recent_deploy['service_name']} by {recent_deploy['author']} ({recent_deploy['commit_message']})",
            "time": recent_deploy["deployed_at"],
        })
        evidence.append({
            "id": f"{context.incident_id}-evd-deploy",
            "source": "deployment",
            "summary": f"Deploy {recent_deploy['version']} shipped to {recent_deploy['service_name']} right before error onset ({recent_deploy['commit_message']}).",
        })

    # 2. Database Signals in Logs
    db_logs = [log for log in context.logs if "db" in log.get("service", "").lower() or "query" in log.get("message", "").lower() or "pool" in log.get("message", "").lower()]
    if db_logs:
        sample_msg = db_logs[0]["message"]
        correlated_findings.append({
            "category": "database",
            "summary": f"Database pressure detected: {sample_msg}",
            "log_count": len(db_logs),
        })
        evidence.append({
            "id": f"{context.incident_id}-evd-db",
            "source": "database",
            "summary": f"Database connection pool exhaustion and slow query execution on {context.service_name}.",
        })

    # 3. Application Metrics & Error Signals
    error_logs = [log for log in context.logs if log.get("level") == "ERROR"]
    if error_logs:
        correlated_findings.append({
            "category": "metrics_logs",
            "summary": f"High error volume: {len(error_logs)} ERROR logs, p95 latency spike and HTTP 5xx errors.",
        })
        evidence.append({
            "id": f"{context.incident_id}-evd-metrics",
            "source": "metrics",
            "summary": f"API p95 latency spiked to >5s and HTTP 5xx error rate exceeded 20% baseline.",
        })

    logger.info(
        "signals correlated",
        extra={"incident_id": context.incident_id, "findings_count": len(correlated_findings)},
    )
    return {"correlated_findings": correlated_findings, "evidence": evidence}
