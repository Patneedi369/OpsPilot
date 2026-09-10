import logging
from datetime import datetime, timezone
from typing import Any

from redis.asyncio import Redis

from app.db.session import SessionLocal
from app.schemas.telemetry import TelemetrySignalIngest
from app.services.detection_service import evaluate_and_correlate, ingest_signal

logger = logging.getLogger("opspilot.worker")

LAST_DETECTION_KEY = "opspilot:last_detection_run"


async def process_telemetry_signal_job(ctx: dict[str, Any], payload_dict: dict[str, Any]) -> str:
    """ARQ background worker job to ingest signal and evaluate detection."""
    payload = TelemetrySignalIngest(**payload_dict)
    async with SessionLocal() as session:
        signal = await ingest_signal(session, payload)
        events = await evaluate_and_correlate(session, service_id=payload.service_id)
        logger.info(
            "process_telemetry_signal_job completed",
            extra={"signal_id": signal.id, "events_count": len(events)},
        )
        return f"signal_id:{signal.id},events:{len(events)}"


async def simulate_incident_detection(ctx: dict[str, Any]) -> str:
    """ARQ background job executing telemetry evaluation across all active signals."""
    redis: Redis = ctx.get("redis")
    timestamp = datetime.now(timezone.utc).isoformat()
    if redis:
        await redis.set(LAST_DETECTION_KEY, timestamp)
        
    async with SessionLocal() as session:
        events = await evaluate_and_correlate(session, auto_investigate=True)
        logger.info(
            "simulate_incident_detection completed",
            extra={"timestamp": timestamp, "events_count": len(events)},
        )
        return f"timestamp:{timestamp},events:{len(events)}"
