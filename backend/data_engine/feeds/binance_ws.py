"""Binance WebSocket feed — real-time BTC-USD trades with 1-minute candle aggregation."""

import asyncio
import json
from datetime import datetime, timezone

import structlog
import websockets

from shared.database import get_pool
from shared.events import Subject, EventType
from shared.nats_client import get_nats
from shared.questdb import questdb

logger = structlog.get_logger()

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"
SYMBOL = "BTCUSDT"


class BinanceWSFeed:
    """Connects to Binance trade stream, writes ticks to QuestDB,
    aggregates 1-minute candles, and publishes to NATS."""

    def __init__(self):
        self._running = False
        self._task: asyncio.Task | None = None
        self._candle: dict | None = None
        self._candle_minute: int = -1

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("binance_ws.started", symbol=SYMBOL)

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        # Flush any partial candle on shutdown
        if self._candle:
            await self._flush_candle()
        self._task = None
        logger.info("binance_ws.stopped")

    async def _run_loop(self) -> None:
        """Reconnecting event loop — retries on disconnect."""
        while self._running:
            try:
                async with websockets.connect(BINANCE_WS_URL) as ws:
                    logger.info("binance_ws.connected", url=BINANCE_WS_URL)
                    async for raw in ws:
                        if not self._running:
                            break
                        await self._handle_trade(json.loads(raw))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning("binance_ws.disconnected", error=str(e))
                if self._running:
                    await asyncio.sleep(3)

    async def _handle_trade(self, msg: dict) -> None:
        """Process a single trade message from Binance."""
        price = float(msg["p"])
        qty = float(msg["q"])
        trade_time_ms = msg["T"]
        trade_time = datetime.fromtimestamp(trade_time_ms / 1000, tz=timezone.utc)
        current_minute = trade_time_ms // 60_000

        # Write tick to QuestDB via ILP
        try:
            questdb.send_ilp(
                table="ticks",
                tags={"symbol": SYMBOL, "exchange": "binance"},
                fields={"price": price, "quantity": qty},
                timestamp=trade_time,
            )
        except Exception as e:
            logger.error("binance_ws.ilp_error", error=str(e))

        # Publish tick to NATS
        try:
            nc = await get_nats()
            js = nc.jetstream()
            tick_payload = json.dumps({
                "type": EventType.TICK,
                "symbol": SYMBOL,
                "price": price,
                "quantity": qty,
                "timestamp": trade_time.isoformat(),
            }).encode()
            await js.publish(
                Subject.PRICE_TICK.format(symbol=SYMBOL),
                tick_payload,
            )
        except Exception as e:
            logger.error("binance_ws.nats_error", error=str(e))

        # Aggregate into 1-minute candle
        if current_minute != self._candle_minute:
            # New minute — flush previous candle, start fresh
            if self._candle is not None:
                await self._flush_candle()
            self._candle_minute = current_minute
            self._candle = {
                "timestamp": datetime.fromtimestamp(
                    current_minute * 60, tz=timezone.utc
                ),
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": qty,
            }
        else:
            c = self._candle
            c["high"] = max(c["high"], price)
            c["low"] = min(c["low"], price)
            c["close"] = price
            c["volume"] += qty

    async def _flush_candle(self) -> None:
        """Write completed 1-minute candle to PostgreSQL context.prices."""
        c = self._candle
        if c is None:
            return

        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO context.prices
                        (symbol, asset_class, exchange, timestamp,
                         open, high, low, close, volume, timeframe)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (symbol, timeframe, timestamp) DO UPDATE SET
                        high  = GREATEST(context.prices.high, EXCLUDED.high),
                        low   = LEAST(context.prices.low, EXCLUDED.low),
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume
                    """,
                    SYMBOL,
                    "crypto",
                    "binance",
                    c["timestamp"],
                    c["open"],
                    c["high"],
                    c["low"],
                    c["close"],
                    c["volume"],
                    "1m",
                )
            logger.debug(
                "binance_ws.candle_flushed",
                symbol=SYMBOL,
                ts=c["timestamp"].isoformat(),
                close=c["close"],
            )
        except Exception as e:
            logger.error("binance_ws.candle_write_error", error=str(e))

        # Publish candle event to NATS
        try:
            nc = await get_nats()
            js = nc.jetstream()
            candle_payload = json.dumps({
                "type": EventType.CANDLE,
                "symbol": SYMBOL,
                "timeframe": "1m",
                "open": c["open"],
                "high": c["high"],
                "low": c["low"],
                "close": c["close"],
                "volume": c["volume"],
                "timestamp": c["timestamp"].isoformat(),
            }).encode()
            await js.publish(
                Subject.PRICE_CANDLE.format(symbol=SYMBOL, timeframe="1m"),
                candle_payload,
            )
        except Exception as e:
            logger.error("binance_ws.candle_nats_error", error=str(e))

        self._candle = None
