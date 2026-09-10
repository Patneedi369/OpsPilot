from datetime import datetime, timezone

from app.schemas.investigation import (
    EvidenceItem,
    InvestigationResult,
    RemediationOption,
    RootCause,
)
from app.services.ai.context import InvestigationContext

INC_2043_RESULT = InvestigationResult(
    id="inv-2043",
    incident_id="INC-2043",
    status="complete",
    summary="/orders API SEV-1 is explained by an unindexed history query introduced in deploy #4821.",
    probable_root_cause=(
        "Deploy #4821 introduced an unindexed order-history query that causes full table scans, "
        "exhausting the orders-db connection pool and cascading into API latency and 5xx errors."
    ),
    evidence=[
        EvidenceItem(
            id="evd-1",
            source="deployment",
            summary="Deploy #4821 (21:04:12 UTC) added an order-history query filtering by customer_id and created_at",
        ),
        EvidenceItem(
            id="evd-2",
            source="database",
            summary="No index exists on (customer_id, created_at); the new query triggers a full scan of 14.2M rows",
        ),
        EvidenceItem(
            id="evd-3",
            source="database",
            summary="order_history query time rose from 40ms to 4.9s immediately after the deploy",
        ),
        EvidenceItem(
            id="evd-4",
            source="database",
            summary="orders-db connection pool climbed from 45/200 to 196/200 within 2 minutes as slow queries held connections open",
        ),
        EvidenceItem(
            id="evd-5",
            source="metrics",
            summary="order-service p95 latency and 5xx rate spike onset (21:06) lags the deploy by under 2 minutes",
        ),
    ],
    affected_service="order-service",
    severity="SEV-1",
    confidence=92,
    recommended_remediation=RemediationOption(
        id="rem-index-pool",
        title="Add composite index + raise pool ceiling",
        description="Add an index on orders(customer_id, created_at) and temporarily raise the connection pool ceiling to relieve pressure while the index builds.",
        risk="medium",
        eta_minutes=11,
        recommended=True,
        kind="infrastructure",
    ),
    investigated_at="",
    reasoning=(
        "The new order-history query has no supporting index, forcing a full table scan on a 14M-row table. "
        "Each request now holds a database connection far longer than before, so the connection pool fills up "
        "and subsequent requests queue and time out, which surfaces as both latency and 5xx errors on order-service."
    ),
    root_cause=RootCause(
        summary=(
            "Deploy #4821 introduced an unindexed order-history query that causes full table scans, "
            "exhausting the orders-db connection pool and cascading into API latency and 5xx errors."
        ),
        confidence=92,
        expected_impact_if_unresolved="Checkout funnel degradation continues to worsen as pool exhaustion spreads to other order-service endpoints",
        affected_users_estimate="~18% of active checkout sessions",
        model="claude-sonnet-4-6",
    ),
    remediations=[
        RemediationOption(
            id="rem-rollback-4821",
            title="Rollback deploy #4821",
            description="Revert order-service to the previous release, immediately removing the unindexed query.",
            risk="low",
            eta_minutes=4,
            recommended=False,
            kind="rollback",
        ),
        RemediationOption(
            id="rem-index-pool",
            title="Add composite index + raise pool ceiling",
            description="Add an index on orders(customer_id, created_at) and temporarily raise the connection pool ceiling to relieve pressure while the index builds.",
            risk="medium",
            eta_minutes=11,
            recommended=True,
            kind="infrastructure",
        ),
    ],
    model="claude-sonnet-4-6",
    provider="fallback",
)


def development_fallback(context: InvestigationContext, model: str) -> InvestigationResult:
    from app.services.ai.guardrails import guardrail_validator
    investigated_at = datetime.now(timezone.utc).isoformat()
    if context.incident_id == "INC-2043":
        res = INC_2043_RESULT.model_copy(
            update={"investigated_at": investigated_at, "model": model, "provider": "fallback"}
        )
        return guardrail_validator.validate_and_repair(res, context)

    watch = RemediationOption(
        id=f"{context.incident_id}-watch",
        title="Continue monitoring",
        description="Keep SLO burn alerts armed and close if the window remains stable.",
        risk="low",
        eta_minutes=5,
        recommended=True,
        kind="forward_fix",
    )
    evidence = [
        EvidenceItem(
            id=f"{context.incident_id}-evd-{index + 1}",
            source="logs" if event.get("type") in {"warn", "crit"} else "topology",
            summary=str(event.get("title", "Related signal")),
        )
        for index, event in enumerate(context.events[:5])
    ]
    if not evidence:
        evidence = [
            EvidenceItem(
                id=f"{context.incident_id}-evd-1",
                source="metrics",
                summary=f"Telemetry for {context.incident_id} is available, but no cascading failure pattern is present.",
            )
        ]
    cause = (
        f"{context.incident_id} does not currently exhibit an active cascading production failure "
        f"beyond the recorded {context.service_name} signals."
    )
    raw_res = InvestigationResult(
        id=f"inv-{context.incident_id}",
        incident_id=context.incident_id,
        status="complete",
        summary=cause,
        probable_root_cause=cause,
        evidence=evidence,
        affected_service=context.service_name,
        severity=context.severity,
        confidence=70,
        recommended_remediation=watch,
        investigated_at=investigated_at,
        reasoning=(
            "Signals are consistent with a contained or already-mitigated issue. "
            "No unindexed query plus pool-exhaustion cascade is present in the collected evidence."
        ),
        root_cause=RootCause(
            summary=cause,
            confidence=70,
            expected_impact_if_unresolved="Limited residual user impact",
            affected_users_estimate="contained",
            model=model,
        ),
        remediations=[watch],
        model=model,
        provider="fallback",
    )
    return guardrail_validator.validate_and_repair(raw_res, context)
