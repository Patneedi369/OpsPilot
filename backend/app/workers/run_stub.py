import asyncio
import logging

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.redis import close_redis, get_redis
from app.workers.jobs import LAST_DETECTION_KEY, simulate_incident_detection

logger = logging.getLogger("opspilot.worker")


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    redis = get_redis()
    timestamp = await simulate_incident_detection({"redis": redis})
    stored = await redis.get(LAST_DETECTION_KEY)
    logger.info("stub job verified", extra={"timestamp": timestamp, "stored": stored})
    print(f"stub job ok last_detection_run={stored}")
    await close_redis()


if __name__ == "__main__":
    asyncio.run(main())
