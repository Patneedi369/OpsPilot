from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import AuthenticatedUser, require_role
from app.schemas.telemetry import (
    DetectionEventResponse,
    RunDetectionRequest,
    TelemetrySignalIngest,
    TelemetrySignalResponse,
)
from app.services.audit_service import log_audit
from app.services.detection_service import (
    evaluate_and_correlate,
    ingest_signal,
    list_detections,
    list_signals,
)

router = APIRouter()


@router.post("/signals", response_model=TelemetrySignalResponse)
async def post_signal(
    payload: TelemetrySignalIngest,
    user: AuthenticatedUser = Depends(require_role(["SRE", "Lead"])),
    session: AsyncSession = Depends(get_db),
) -> TelemetrySignalResponse:
    signal = await ingest_signal(session, payload)
    await log_audit(
        session=session,
        user_id=user.id,
        username=user.username,
        user_role=user.role,
        action="telemetry.signal_ingested",
        resource_type="signal",
        resource_id=signal.id,
        outcome="success",
        metadata={"metric": signal.metric, "service_id": signal.service_id, "value": signal.value},
    )
    return signal


@router.post("/detect", response_model=list[DetectionEventResponse])
async def trigger_detection(
    payload: RunDetectionRequest = RunDetectionRequest(),
    user: AuthenticatedUser = Depends(require_role(["SRE", "Lead"])),
    session: AsyncSession = Depends(get_db),
) -> list[DetectionEventResponse]:
    events = await evaluate_and_correlate(
        session=session,
        service_id=payload.service_id,
        auto_investigate=payload.auto_investigate,
    )
    await log_audit(
        session=session,
        user_id=user.id,
        username=user.username,
        user_role=user.role,
        action="telemetry.detection_triggered",
        resource_type="detection",
        resource_id=payload.service_id or "all_services",
        outcome="success",
        metadata={"events_created": len(events)},
    )
    return events


@router.get("/signals", response_model=list[TelemetrySignalResponse])
async def get_signals(
    service_id: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
) -> list[TelemetrySignalResponse]:
    return await list_signals(session, service_id)


@router.get("/detections", response_model=list[DetectionEventResponse])
async def get_detections(
    incident_id: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
) -> list[DetectionEventResponse]:
    return await list_detections(session, incident_id)
