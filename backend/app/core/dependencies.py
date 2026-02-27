
from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.cache import CacheService
from app.database import async_session_factory

_redis_client: Redis | None = None


async def get_redis() -> Redis | None:
    global _redis_client
    if _redis_client is None:
        try:
            client = Redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            await client.ping()
            _redis_client = client
        except Exception:
            import logging
            logging.getLogger(__name__).warning("Redis unavailable — running without cache")
            return None
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_cache() -> CacheService:
    redis = await get_redis()
    return CacheService(redis)
