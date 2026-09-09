from arq.connections import RedisSettings

from app.core.config import get_settings
from app.workers.jobs import simulate_incident_detection


def _redis_settings() -> RedisSettings:
    return RedisSettings.from_dsn(get_settings().redis_url)


class WorkerSettings:
    functions = [simulate_incident_detection]
    redis_settings = _redis_settings()
    max_jobs = 5
