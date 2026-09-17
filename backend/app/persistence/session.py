from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

import logging

logger = logging.getLogger("opspilot.db")

settings = get_settings()

if "db." in settings.database_url and ".supabase.co" in settings.database_url:
    logger.warning(
        "Direct Supabase hostname detected in DATABASE_URL. "
        "Free cloud hosts like Render require IPv4 Supabase Connection Pooler host (aws-0-*.pooler.supabase.com:6543) "
        "to avoid 'OSError: [Errno 101] Network is unreachable'."
    )

engine = create_async_engine(
    settings.database_url,
    connect_args={"statement_cache_size": 0},
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=30,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
