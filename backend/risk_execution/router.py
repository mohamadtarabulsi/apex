"""FastAPI router for Risk & Execution Engine endpoints."""

import json

from fastapi import APIRouter

from shared.database import get_pool
from shared.models import RiskStateRecord

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/risk", tags=["risk-execution"])


@router.get("/state")
async def get_risk():
    """Current risk metrics — latest risk_state snapshot."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM context.risk_state ORDER BY timestamp DESC LIMIT 1"
            )
            if not row:
                return {
                    "portfolio_heat": 0.0,
                    "var_95": 0.0,
                    "cvar_95": 0.0,
                    "current_drawdown": 0.0,
                    "max_drawdown": 0.0,
                    "open_positions": 0,
                    "daily_pnl": 0.0,
                    "leverage": 0.0,
                }
            return RiskStateRecord(
                id=row["id"],
                portfolio_heat=row["portfolio_heat"],
                var_95=row["var_95"],
                cvar_95=row["cvar_95"],
                current_drawdown=row["current_drawdown"],
                max_drawdown=row["max_drawdown"],
                realized_vol=row["realized_vol"],
                target_vol=row["target_vol"],
                leverage=row["leverage"],
                open_positions=row["open_positions"],
                daily_pnl=row["daily_pnl"],
                weekly_pnl=row["weekly_pnl"],
                risk_limits=json.loads(row["risk_limits"]) if row["risk_limits"] else None,
                timestamp=row["timestamp"],
                created_at=row["created_at"],
            )
    except Exception as e:
        logger.error("risk.fetch_error", error=str(e))
        return {"error": str(e)}


@router.get("/portfolio")
async def get_portfolio():
    """Current portfolio state — open trades and summary."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            trades = await conn.fetch(
                """
                SELECT * FROM context.trades
                WHERE status = 'open'
                ORDER BY created_at DESC
                """
            )
            total_pnl = await conn.fetchval(
                "SELECT COALESCE(SUM(pnl), 0) FROM context.trades WHERE status = 'closed'"
            )
            return {
                "open_positions": len(trades),
                "total_realized_pnl": float(total_pnl),
                "trades": [dict(r) for r in trades],
            }
    except Exception as e:
        logger.error("portfolio.fetch_error", error=str(e))
        return {"open_positions": 0, "total_realized_pnl": 0.0, "trades": []}
