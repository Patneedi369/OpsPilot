import asyncio
import logging
import sys

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import get_settings

logger = logging.getLogger("opspilot.graph.checkpointer")

_global_pool = None
_global_memory_saver = MemorySaver()


def _ensure_windows_selector_policy() -> None:
    if sys.platform == "win32":
        try:
            policy = asyncio.get_event_loop_policy()
            if not isinstance(policy, asyncio.WindowsSelectorEventLoopPolicy):
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            pass


async def get_checkpointer() -> BaseCheckpointSaver:
    global _global_pool

    _ensure_windows_selector_policy()
    settings = get_settings()
    db_url = (
        settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        .replace("ssl=require", "sslmode=require")
    )

    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
        from psycopg_pool import AsyncConnectionPool

        serializer = JsonPlusSerializer(allowed_msgpack_modules=True)

        if _global_pool is None:
            _global_pool = AsyncConnectionPool(
                conninfo=db_url,
                kwargs={"autocommit": True, "prepare_threshold": None},
                min_size=1,
                max_size=10,
                open=False,
            )
            await _global_pool.open()
            setup_checkpointer = AsyncPostgresSaver(_global_pool, serde=serializer)
            await setup_checkpointer.setup()

        return AsyncPostgresSaver(_global_pool, serde=serializer)
    except Exception:
        logger.exception("Failed to initialize AsyncPostgresSaver; falling back to MemorySaver")
        return _global_memory_saver
