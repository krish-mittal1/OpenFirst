
import hashlib
import json
import logging
from typing import Any, Callable, Awaitable

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class CacheService:

    def __init__(self, redis: Redis | None):
        self.redis = redis

    async def _is_available(self) -> bool:
        if self.redis is None:
            return False
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False

    async def get(self, key: str) -> Any | None:
        try:
            if not self.redis:
                return None
            raw = await self.redis.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = 900) -> None:
        try:
            if not self.redis:
                return
            serialized = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized)
        except Exception:
            logger.debug("Cache SET failed (Redis unavailable): %s", key)

    async def get_or_set(
        self,
        key: str,
        ttl: int,
        factory: Callable[[], Awaitable[Any]],
    ) -> Any:
        cached = await self.get(key)
        if cached is not None:
            logger.debug("Cache HIT: %s", key)
            return cached

        logger.debug("Cache MISS: %s", key)
        result = await factory()

        await self.set(key, result, ttl)
        return result

    async def invalidate(self, key: str) -> None:
        try:
            if self.redis:
                await self.redis.delete(key)
        except Exception:
            pass

    async def invalidate_pattern(self, pattern: str) -> int:
        try:
            if not self.redis:
                return 0
            keys: list[str] = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info("Invalidated %d keys matching '%s'", deleted, pattern)
                return deleted
        except Exception:
            pass
        return 0

    @staticmethod
    def hash_params(params: dict) -> str:
        normalized = json.dumps(
            {k: v for k, v in sorted(params.items()) if v is not None},
            sort_keys=True,
        )
        return hashlib.md5(normalized.encode()).hexdigest()[:12]
