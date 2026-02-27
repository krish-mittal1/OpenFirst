
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.core.dependencies import get_redis
from app.services.github_client import github_client

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(
    redis: Redis = Depends(get_redis),
):
    health = {
        "status": "healthy",
        "redis": "unknown",
        "github_rate_remaining": github_client.rate_remaining,
    }

    if redis is None:
        health["redis"] = "unavailable (running without cache)"
    else:
        try:
            await redis.ping()
            health["redis"] = "connected"
        except Exception as e:
            health["redis"] = f"error: {e}"
            health["status"] = "degraded"

    return health
