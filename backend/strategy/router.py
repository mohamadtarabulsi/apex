"""FastAPI router for Strategy Engine endpoints."""

import json
from uuid import UUID

from fastapi import APIRouter, Query

from shared.database import get_pool
from shared.models import SignalRecord

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/strategy", tags=["strategy"])


@router.get("/signals")
async def get_signals(
    status: str | None = Query(None, description="Filter by status"),
    strategy: str | None = Query(None, description="Filter by strategy"),
    limit: int = Query(50, ge=1, le=500),
):
    """Recent signals with optional filters."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            query = "SELECT * FROM context.signals WHERE 1=1"
            params = []
            idx = 1

            if status:
                query += f" AND status = ${idx}"
                params.append(status)
                idx += 1
            if strategy:
                query += f" AND strategy = ${idx}"
                params.append(strategy)
                idx += 1

            query += f" ORDER BY timestamp DESC LIMIT ${idx}"
            params.append(limit)

            rows = await conn.fetch(query, *params)
            return [
                SignalRecord(
                    id=r["id"],
                    signal_id=r["signal_id"],
                    symbol=r["symbol"],
                    asset_class=r["asset_class"],
                    strategy=r["strategy"],
                    direction=r["direction"],
                    confidence=r["confidence"],
                    risk_reward=r["risk_reward"],
                    entry_price=r["entry_price"],
                    stop_loss=r["stop_loss"],
                    take_profit=r["take_profit"],
                    reasoning=r["reasoning"],
                    regime_state=r["regime_state"],
                    factors=json.loads(r["factors"]) if r["factors"] else None,
                    status=r["status"],
                    timestamp=r["timestamp"],
                    created_at=r["created_at"],
                )
                for r in rows
            ]
    except Exception as e:
        logger.error("signals.fetch_error", error=str(e))
        return []


@router.get("/signals/{signal_id}")
async def get_signal(signal_id: str):
    """Single signal detail by UUID."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM context.signals WHERE signal_id = $1",
                UUID(signal_id),
            )
            if not row:
                return {"error": "Signal not found"}
            return SignalRecord(
                id=row["id"],
                signal_id=row["signal_id"],
                symbol=row["symbol"],
                asset_class=row["asset_class"],
                strategy=row["strategy"],
                direction=row["direction"],
                confidence=row["confidence"],
                risk_reward=row["risk_reward"],
                entry_price=row["entry_price"],
                stop_loss=row["stop_loss"],
                take_profit=row["take_profit"],
                reasoning=row["reasoning"],
                regime_state=row["regime_state"],
                factors=json.loads(row["factors"]) if row["factors"] else None,
                status=row["status"],
                timestamp=row["timestamp"],
                created_at=row["created_at"],
            )
    except Exception as e:
        logger.error("signal.fetch_error", signal_id=signal_id, error=str(e))
        return {"error": str(e)}


@router.get("/predictions")
async def get_predictions(
    platform: str | None = Query(None),
    resolved: bool = Query(False),
    limit: int = Query(50, ge=1, le=500),
):
    """Active prediction market positions."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            query = "SELECT * FROM context.predictions WHERE resolved = $1"
            params: list = [resolved]
            idx = 2

            if platform:
                query += f" AND platform = ${idx}"
                params.append(platform)
                idx += 1

            query += f" ORDER BY edge DESC NULLS LAST LIMIT ${idx}"
            params.append(limit)

            rows = await conn.fetch(query, *params)
            return [dict(r) for r in rows]
    except Exception as e:
        logger.error("predictions.fetch_error", error=str(e))
        return []
