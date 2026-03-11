"""Redis client — pub/sub, streams, and caching."""

import redis.asyncio as aioredis
import structlog

from shared.config import settings

logger = structlog.get_logger()

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get or create the async Redis client."""
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("Redis client created", url=settings.redis_url)
    return _redis


async def close_redis() -> None:
    """Close the Redis connection."""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
        logger.info("Redis client closed")


async def check_redis() -> dict:
    """Health check — ping Redis."""
    try:
        r = await get_redis()
        pong = await r.ping()
        info = await r.info("server")
        return {
            "status": "healthy" if pong else "unhealthy",
            "version": info.get("redis_version", "unknown"),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
