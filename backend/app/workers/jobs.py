import logging
from datetime import datetime, timezone
from typing import Any

from redis.asyncio import Redis

logger = logging.getLogger("opspilot.worker")

LAST_DETECTION_KEY = "opspilot:last_detection_run"


async def simulate_incident_detection(ctx: dict[str, Any]) -> str:
    """Stub job: records a timestamp only. Real detection comes in a later phase."""
    redis: Redis = ctx["redis"]
    timestamp = datetime.now(timezone.utc).isoformat()
    await redis.set(LAST_DETECTION_KEY, timestamp)
    logger.info("simulate_incident_detection completed", extra={"timestamp": timestamp})
    return timestamp
