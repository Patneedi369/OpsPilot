import logging
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.persistence.session import get_db
from app.schemas.incident import HealthResponse

router = APIRouter()
logger = logging.getLogger("opspilot.api.health")


@router.get("/health", response_model=HealthResponse)
async def get_health(
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> HealthResponse:
    settings = get_settings()
    components: dict[str, str] = {}
    is_healthy = True

    # 1. Check PostgreSQL (Primary data store)
    try:
        await session.execute(text("SELECT 1"))
        components["postgres"] = "healthy"
    except Exception as exc:
        logger.error("health check: postgres unhealthy", extra={"error": str(exc)})
        components["postgres"] = "unhealthy"
        is_healthy = False

    # 2. Check Redis (Cache / Worker queue)
    try:
        redis = get_redis()
        pong = await redis.ping()
        components["redis"] = "healthy" if pong else "degraded"
    except Exception as exc:
        logger.info("health check: redis unreached", extra={"error": str(exc)})
        components["redis"] = "degraded"

    # 3. Check Worker status
    try:
        redis = get_redis()
        last_run = await redis.get("opspilot:last_detection_run")
        components["worker"] = "active" if last_run else "idle"
    except Exception:
        components["worker"] = "idle"

    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(status="unhealthy", service=settings.app_name, components=components)

    return HealthResponse(status="ok", service=settings.app_name, components=components)


@router.get("/health/readiness", response_model=HealthResponse)
async def get_readiness(
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> HealthResponse:
    return await get_health(response=response, session=session)
