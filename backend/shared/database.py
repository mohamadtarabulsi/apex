"""PostgreSQL connection pool using asyncpg with SQLAlchemy async engine."""

import asyncpg
import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from shared.config import settings

logger = structlog.get_logger()

# SQLAlchemy async engine
engine = create_async_engine(
    settings.postgres_dsn,
    pool_size=20,
    max_overflow=10,
    echo=False,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Raw asyncpg pool for direct queries
_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the asyncpg connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=settings.postgres_host,
            port=settings.postgres_port,
            database=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            min_size=5,
            max_size=20,
        )
        logger.info("asyncpg pool created", host=settings.postgres_host, db=settings.postgres_db)
    return _pool


async def close_pool() -> None:
    """Close the asyncpg connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("asyncpg pool closed")


async def check_postgres() -> dict:
    """Health check — returns version and connection count."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
            count = await conn.fetchval("SELECT count(*) FROM context.signals")
            return {"status": "healthy", "version": version, "signals_count": count}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
