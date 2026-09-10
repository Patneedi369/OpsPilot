import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.detection_event import DetectionEvent
from app.models.incident import Incident
from app.models.telemetry_signal import TelemetrySignal
from app.schemas.telemetry import TelemetrySignalIngest
from app.services.investigation_service import investigate_incident

logger = logging.getLogger("opspilot.services.detection")

ACTIVE_INCIDENT_STATUSES = {
    "detected",
    "investigating",
    "awaiting_approval",
    "executing",
    "verifying",
    "monitoring",
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def ingest_signal(session: AsyncSession, payload: TelemetrySignalIngest) -> TelemetrySignal:
    signal_id = f"sig-{uuid.uuid4().hex[:8]}"
    signal = TelemetrySignal(
        id=signal_id,
        metric=payload.metric,
        value=payload.value,
        threshold=payload.threshold,
        service_id=payload.service_id,
        source=payload.source,
        status="active",
        metadata_json=payload.metadata,
        created_at=utcnow(),
    )
    session.add(signal)
    await session.commit()
    await session.refresh(signal)
    logger.info("telemetry signal ingested", extra={"signal_id": signal.id, "metric": signal.metric, "service_id": signal.service_id})
    return signal


async def evaluate_and_correlate(
    session: AsyncSession,
    service_id: str | None = None,
    auto_investigate: bool = True,
) -> list[DetectionEvent]:
    query = select(TelemetrySignal).where(TelemetrySignal.status == "active")
    if service_id:
        query = query.where(TelemetrySignal.service_id == service_id)
    
    res = await session.execute(query)
    signals = list(res.scalars().all())
    if not signals:
        return []

    # Filter signals that breach threshold or are event signals
    breached_signals: list[TelemetrySignal] = []
    for sig in signals:
        is_breach = False
        if sig.metric in ["api_latency_ms", "5xx_error_rate", "db_query_duration_ms", "pool_utilization"]:
            is_breach = sig.value >= sig.threshold
        elif sig.metric in ["deployment_event", "error_log"]:
            is_breach = True
        else:
            is_breach = sig.value >= sig.threshold

        if is_breach:
            breached_signals.append(sig)

    if not breached_signals:
        return []

    # Group breached signals by target service
    by_service: dict[str, list[TelemetrySignal]] = {}
    for sig in breached_signals:
        by_service.setdefault(sig.service_id, []).append(sig)

    detection_events: list[DetectionEvent] = []

    for svc_id, svc_signals in by_service.items():
        # Check for active incident for this service
        inc_stmt = select(Incident).where(
            Incident.service_id == svc_id,
            Incident.status.in_(ACTIVE_INCIDENT_STATUSES),
        )
        inc_res = await session.execute(inc_stmt)
        active_incident = inc_res.scalars().first()

        rule_name = f"THRESHOLD_BREACH_{svc_id.upper().replace('-', '_')}"
        summary = (
            f"Correlated {len(svc_signals)} signals breaching threshold on {svc_id}: "
            + ", ".join(f"{s.metric}={s.value}" for s in svc_signals[:3])
        )

        if active_incident:
            target_incident = active_incident
            target_incident_id = active_incident.id
            logger.info(
                "correlating signals into existing active incident",
                extra={"incident_id": target_incident_id, "service_id": svc_id, "signals_count": len(svc_signals)},
            )
        else:
            # Check if this is explicitly the INC-2043 scenario (orders service)
            is_inc2043 = svc_id in ["orders-service", "order-service"]
            if is_inc2043:
                existing_2043_res = await session.execute(select(Incident).where(Incident.id == "INC-2043"))
                inc_2043 = existing_2043_res.scalars().first()
                if inc_2043:
                    target_incident_id = "INC-2043"
                else:
                    target_incident_id = f"INC-{uuid.uuid4().hex[:4].upper()}"
            else:
                target_incident_id = f"INC-{uuid.uuid4().hex[:4].upper()}"

            # If incident doesn't exist at all, create it
            inc_lookup = await session.execute(select(Incident).where(Incident.id == target_incident_id))
            target_incident = inc_lookup.scalars().first()

            if not target_incident:
                target_incident = Incident(
                    id=target_incident_id,
                    title=f"Automated Alert: High Latency & Resource Exhaustion on {svc_id}",
                    severity="SEV-1",
                    status="detected",
                    workflow_stage="detection",
                    service_id=svc_id,
                    service_name=svc_id.replace("-", " ").title(),
                    started_at=utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    duration_label="just now",
                    elapsed_seconds=0,
                    trigger=summary,
                    affected_services=[svc_id],
                    blast_radius="High impact on latency and API availability",
                    created_at=utcnow(),
                )
                session.add(target_incident)
                await session.flush()

        # Link signals to incident
        for s in svc_signals:
            s.incident_id = target_incident_id
            s.status = "correlated"

        event_id = f"evt-{uuid.uuid4().hex[:8]}"
        detection_event = DetectionEvent(
            id=event_id,
            incident_id=target_incident_id,
            rule_name=rule_name,
            summary=summary,
            correlated_signals_count=len(svc_signals),
            metadata_json={"service_id": svc_id, "signals": [s.id for s in svc_signals]},
            created_at=utcnow(),
        )
        session.add(detection_event)
        detection_events.append(detection_event)

        # Publish real-time SSE event
        from app.core.events import event_bus
        event_bus.publish(
            incident_id=target_incident_id,
            event_type="incident_detected",
            payload={"rule_name": rule_name, "summary": summary, "service_id": svc_id},
            status="detected",
        )

        # Trigger workflow if auto_investigate is requested
        if auto_investigate:
            try:
                await investigate_incident(session, target_incident_id)
                target_incident.status = "awaiting_approval"
                target_incident.workflow_stage = "remediation_proposal"
            except Exception as exc:
                logger.warning(
                    "failed to auto-trigger investigation workflow after detection",
                    extra={"incident_id": target_incident_id, "error": str(exc)},
                )

    await session.commit()
    for evt in detection_events:
        await session.refresh(evt)

    return detection_events


async def list_signals(session: AsyncSession, service_id: str | None = None) -> list[TelemetrySignal]:
    stmt = select(TelemetrySignal)
    if service_id:
        stmt = stmt.where(TelemetrySignal.service_id == service_id)
    stmt = stmt.order_by(TelemetrySignal.created_at.desc())
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def list_detections(session: AsyncSession, incident_id: str | None = None) -> list[DetectionEvent]:
    stmt = select(DetectionEvent)
    if incident_id:
        stmt = stmt.where(DetectionEvent.incident_id == incident_id)
    stmt = stmt.order_by(DetectionEvent.created_at.desc())
    res = await session.execute(stmt)
    return list(res.scalars().all())
