"""APEX — Main FastAPI application. Single process running all 4 service modules."""

import json
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.database import check_postgres, close_pool, get_pool
from shared.questdb import questdb
from shared.redis_client import check_redis, close_redis
from shared.nats_client import check_nats, close_nats
from shared.models import (
    HealthStatus,
    PriceRecord,
    RiskStateRecord,
    SignalRecord,
    SystemHealth,
)

from data_engine import data_engine
from intelligence import intelligence_engine
from strategy import strategy_engine
from risk_execution import risk_execution_engine

from data_engine.router import router as data_router
from intelligence.router import router as intelligence_router
from strategy.router import router as strategy_router
from risk_execution.router import router as risk_router

logger = structlog.get_logger()

START_TIME = time.time()


# --- WebSocket manager ---
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: dict):
        data = json.dumps(message, default=str)
        for ws in self.active[:]:
            try:
                await ws.send_text(data)
            except Exception:
                self.active.remove(ws)


ws_manager = ConnectionManager()


# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("apex.starting", environment=settings.environment)
    # Start all service modules
    await data_engine.start()
    await intelligence_engine.start()
    await strategy_engine.start()
    await risk_execution_engine.start()
    logger.info("apex.all_services_started")
    yield
    # Shutdown
    logger.info("apex.shutting_down")
    await data_engine.stop()
    await intelligence_engine.stop()
    await strategy_engine.stop()
    await risk_execution_engine.stop()
    questdb.close()
    await close_pool()
    await close_redis()
    await close_nats()
    logger.info("apex.shutdown_complete")


app = FastAPI(
    title="APEX",
    description="AI-Powered Quantitative Trading System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include module routers ---
app.include_router(data_router)
app.include_router(intelligence_router)
app.include_router(strategy_router)
app.include_router(risk_router)


# --- Health endpoints ---


@app.get("/health")
async def health():
    """System health — quick check of all services."""
    pg = await check_postgres()
    rd = await check_redis()
    nt = await check_nats()
    qdb = await questdb.health()

    all_healthy = all(
        s.get("status") == "healthy" for s in [pg, rd, nt, qdb]
    )

    return SystemHealth(
        status="healthy" if all_healthy else "degraded",
        uptime_seconds=round(time.time() - START_TIME, 1),
        services={
            "postgres": HealthStatus(service="postgres", status=pg["status"], details=pg),
            "redis": HealthStatus(service="redis", status=rd["status"], details=rd),
            "nats": HealthStatus(service="nats", status=nt["status"], details=nt),
            "questdb": HealthStatus(service="questdb", status=qdb["status"], details=qdb),
        },
    )


@app.get("/api/v1/status")
async def detailed_status():
    """Detailed status of every service and infrastructure component."""
    pg = await check_postgres()
    rd = await check_redis()
    nt = await check_nats()
    qdb = await questdb.health()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "environment": settings.environment,
        "infrastructure": {
            "postgres": pg,
            "redis": rd,
            "nats": nt,
            "questdb": qdb,
        },
        "services": {
            "data_engine": data_engine.status(),
            "intelligence": intelligence_engine.status(),
            "strategy": strategy_engine.status(),
            "risk_execution": risk_execution_engine.status(),
        },
    }


# --- Top-level convenience endpoints (preserve existing API paths) ---


@app.get("/api/v1/prices/{symbol}")
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


@app.get("/api/v1/signals")
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


@app.get("/api/v1/signals/{signal_id}")
async def get_signal(signal_id: str):
    """Single signal detail by UUID."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            from uuid import UUID
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


@app.get("/api/v1/portfolio")
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


@app.get("/api/v1/risk")
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


@app.get("/api/v1/calibration")
async def get_calibration():
    """Calibration dashboard data — model performance metrics."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT ON (model_name, metric_type)
                    model_name, asset_class, metric_type, metric_value,
                    bucket, category, sample_size, details, timestamp
                FROM context.calibration
                ORDER BY model_name, metric_type, timestamp DESC
                """
            )
            return [dict(r) for r in rows]
    except Exception as e:
        logger.error("calibration.fetch_error", error=str(e))
        return []


@app.get("/api/v1/predictions")
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


# --- WebSocket ---


@app.websocket("/ws/feed")
async def websocket_feed(ws: WebSocket):
    """Real-time feed — pushes prices, signals, and status updates."""
    await ws_manager.connect(ws)
    try:
        # Send initial status on connect
        await ws.send_text(
            json.dumps(
                {
                    "type": "status",
                    "data": {
                        "connected": True,
                        "uptime": round(time.time() - START_TIME, 1),
                        "services": {
                            "data_engine": data_engine.status(),
                            "intelligence": intelligence_engine.status(),
                            "strategy": strategy_engine.status(),
                            "risk_execution": risk_execution_engine.status(),
                        },
                    },
                },
                default=str,
            )
        )
        # Keep alive and listen for client messages
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await ws.send_text(json.dumps({"type": "pong", "ts": datetime.now(timezone.utc).isoformat()}))
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception:
        ws_manager.disconnect(ws)
