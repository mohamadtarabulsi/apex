"""FastAPI router for Data Engine endpoints."""

import json

from fastapi import APIRouter, Query

from shared.database import get_pool
from shared.models import PriceRecord

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/data", tags=["data-engine"])


@router.get("/prices/{symbol}")
async def get_prices(
    symbol: str,
    timeframe: str = Query("1H", description="Candle timeframe"),
    limit: int = Query(100, ge=1, le=1000),
):
    """Latest prices for a symbol from context.prices."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, symbol, asset_class, exchange, timestamp,
                       open, high, low, close, volume, timeframe, indicators, created_at
                FROM context.prices
                WHERE symbol = $1 AND timeframe = $2
                ORDER BY timestamp DESC
                LIMIT $3
                """,
                symbol.upper(),
                timeframe,
                limit,
            )
            return [
                PriceRecord(
                    id=r["id"],
                    symbol=r["symbol"],
                    asset_class=r["asset_class"],
                    exchange=r["exchange"],
                    timestamp=r["timestamp"],
                    open=r["open"],
                    high=r["high"],
                    low=r["low"],
                    close=r["close"],
                    volume=r["volume"],
                    timeframe=r["timeframe"],
                    indicators=json.loads(r["indicators"]) if r["indicators"] else None,
                    created_at=r["created_at"],
                )
                for r in rows
            ]
    except Exception as e:
        logger.error("prices.fetch_error", symbol=symbol, error=str(e))
        return []
