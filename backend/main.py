"""APEX — Main FastAPI application. Single process running all 4 service modules."""

import asyncio
import json
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.database import check_postgres, close_pool
from shared.questdb import questdb
from shared.redis_client import check_redis, close_redis
from shared.nats_client import check_nats, close_nats, get_nats
from shared.models import HealthStatus, SystemHealth

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
async def _nats_price_forwarder():
    """Subscribe to NATS price ticks and broadcast to WebSocket clients."""
    try:
        nc = await get_nats()
        js = nc.jetstream()
        sub = await js.subscribe("prices.>", durable="ws_price_forwarder")
        async for msg in sub.messages:
            try:
                payload = json.loads(msg.data.decode())
                await ws_manager.broadcast({"type": "price", "data": payload})
                await msg.ack()
            except Exception:
                await msg.ack()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error("nats_price_forwarder.error", error=str(e))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("apex.starting", environment=settings.environment)
    await data_engine.start()
    await intelligence_engine.start()
    await strategy_engine.start()
    await risk_execution_engine.start()

    # Start NATS -> WebSocket price forwarder
    forwarder_task = asyncio.create_task(_nats_price_forwarder())

    logger.info("apex.all_services_started")
    yield
    logger.info("apex.shutting_down")

    forwarder_task.cancel()
    try:
        await forwarder_task
    except asyncio.CancelledError:
        pass

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

# --- Module routers (all endpoints live here, no duplicates) ---
app.include_router(data_router)
app.include_router(intelligence_router)
app.include_router(strategy_router)
app.include_router(risk_router)


# --- Health & status (system-level, not module-specific) ---


@app.get("/health")
async def health():
    """System health — quick check of all infrastructure."""
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
    """Detailed status of every module and infrastructure component."""
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
        "modules": {
            "data_engine": data_engine.status(),
            "intelligence": intelligence_engine.status(),
            "strategy": strategy_engine.status(),
            "risk_execution": risk_execution_engine.status(),
        },
    }


# --- WebSocket ---


@app.websocket("/ws/feed")
async def websocket_feed(ws: WebSocket):
    """Real-time feed — pushes prices, signals, and status updates."""
    await ws_manager.connect(ws)
    try:
        await ws.send_text(
            json.dumps(
                {
                    "type": "status",
                    "data": {
                        "connected": True,
                        "uptime": round(time.time() - START_TIME, 1),
                        "modules": {
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
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await ws.send_text(
                    json.dumps({"type": "pong", "ts": datetime.now(timezone.utc).isoformat()})
                )
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception:
        ws_manager.disconnect(ws)
