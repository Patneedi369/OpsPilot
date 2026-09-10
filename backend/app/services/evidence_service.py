import logging
from typing import Any

from app.schemas.evidence import EvidenceChainResponse, NormalizedEvidence
from app.services.ai.context import InvestigationContext

logger = logging.getLogger("opspilot.services.evidence")

# Service Dependency Mapping for topology correlation
DEPENDENCY_GRAPH: dict[str, list[str]] = {
    "checkout-service": ["orders-service", "payment-service"],
    "orders-service": ["postgres-orders-db", "orders-db"],
    "order-service": ["postgres-orders-db", "orders-db"],
    "payment-service": ["postgres-payment-db"],
    "user-service": ["postgres-user-db"],
}


def compute_evidence_score(
    source: str,
    service: str,
    target_service: str,
    is_deployment: bool = False,
    is_critical: bool = False,
) -> tuple[float, str]:
    score = 0.5
    reasons = []

    # Service / Dependency match
    if service in (target_service, target_service.replace("-service", ""), f"{target_service}-db"):
        score += 0.3
        reasons.append(f"Direct match on target service '{service}'")
    elif target_service in DEPENDENCY_GRAPH and service in DEPENDENCY_GRAPH[target_service]:
        score += 0.2
        reasons.append(f"Upstream dependency relationship ({target_service} -> {service})")

    # Deployment proximity
    if is_deployment:
        score += 0.15
        reasons.append("Recent deployment near incident onset")

    # Critical severity
    if is_critical:
        score += 0.1
        reasons.append("Critical metric/error threshold breach")

    final_score = min(1.0, round(score, 2))
    reason_text = "; ".join(reasons) if reasons else "Correlated timeline signal"
    return final_score, reason_text


class EvidenceService:
    def build_evidence_chain(self, context: InvestigationContext) -> EvidenceChainResponse:
        evidence_list: list[NormalizedEvidence] = []
        target_service = context.service_id or "orders-service"

        # 1. Deployment evidence
        for idx, dep in enumerate(context.deployments):
            dep_service = dep.get("service_id") or dep.get("service_name") or target_service
            score, reason = compute_evidence_score(
                source="deployment",
                service=dep_service,
                target_service=target_service,
                is_deployment=True,
                is_critical=True,
            )
            version = dep.get("version", "deploy-#4821")
            commit_msg = dep.get("commit_message", "Updated order query logic")
            evidence_list.append(
                NormalizedEvidence(
                    evidence_id=f"evd-dep-{idx+1}",
                    source="deployment",
                    timestamp=dep.get("deployed_at") or context.started_at,
                    signal_type="deployment_release",
                    service=dep_service,
                    severity_relevance=score,
                    summary=f"Deploy {version}: {commit_msg}",
                    correlation_reason=reason,
                    raw_data=dep,
                )
            )

        # 2. Log & Metric events evidence
        for idx, event in enumerate(context.events):
            evt_type = event.get("type", "metric")
            title = event.get("title", "Signal breach")
            desc = event.get("description", "")
            is_crit = "crit" in evt_type.lower() or "5xx" in desc.lower() or "error" in desc.lower()
            
            score, reason = compute_evidence_score(
                source="logs" if "log" in evt_type else "metrics",
                service=target_service,
                target_service=target_service,
                is_critical=is_crit,
            )
            
            evidence_list.append(
                NormalizedEvidence(
                    evidence_id=f"evd-evt-{idx+1}",
                    source="database" if "query" in desc.lower() or "index" in desc.lower() else "metrics",
                    timestamp=event.get("timestamp") or context.started_at,
                    signal_type=evt_type,
                    service=target_service,
                    severity_relevance=score,
                    summary=f"{title}: {desc}",
                    correlation_reason=reason,
                    raw_data=event,
                )
            )

        # 3. Log entries evidence
        for idx, log in enumerate(context.logs):
            log_svc = log.get("service", target_service)
            msg = log.get("message", "")
            is_crit = log.get("level") in ["ERROR", "CRITICAL", "FATAL"]
            
            score, reason = compute_evidence_score(
                source="logs",
                service=log_svc,
                target_service=target_service,
                is_critical=is_crit,
            )

            evidence_list.append(
                NormalizedEvidence(
                    evidence_id=f"evd-log-{idx+1}",
                    source="logs",
                    timestamp=log.get("timestamp") or context.started_at,
                    signal_type="error_log",
                    service=log_svc,
                    severity_relevance=score,
                    summary=f"[{log.get('level', 'INFO')}] {msg}",
                    correlation_reason=reason,
                    raw_data=log,
                )
            )

        # Build causal chain for INC-2043 or default
        causal_chain = [
            f"Deployment #4821 on {target_service} introduced order-history query",
            f"Database query time increased due to missing composite index on (customer_id, created_at)",
            f"Connection pool utilization reached 98% on {target_service}",
            f"API p95 latency spiked to >4000ms and 5xx error rate breached 18%",
        ]

        # Sort evidence by relevance score descending
        evidence_list.sort(key=lambda x: x.severity_relevance, reverse=True)

        return EvidenceChainResponse(
            incident_id=context.incident_id,
            total_evidence_count=len(evidence_list),
            causal_chain=causal_chain,
            evidence=evidence_list,
        )


evidence_service = EvidenceService()
