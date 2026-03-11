"""Data Engine service — manages all market data ingestion pipelines."""

import structlog

from data_engine.feeds.binance_ws import BinanceWSFeed

logger = structlog.get_logger()


class DataEngine:
    """Manages WebSocket feeds, REST polling, and indicator computation."""

    def __init__(self):
        self.feeds: dict[str, bool] = {}
        self._running = False
        self._binance_ws = BinanceWSFeed()

    async def start(self) -> None:
        """Initialize data feeds and start ingestion loops."""
        self._running = True
        self.feeds = {
            "binance_ws": False,
            "alpaca_ws": False,
            "kalshi_rest": False,
            "polymarket_rest": False,
        }

        # Start the Binance WebSocket feed
        try:
            await self._binance_ws.start()
            self.feeds["binance_ws"] = True
        except Exception as e:
            logger.error("data_engine.binance_ws_start_failed", error=str(e))

        logger.info("data_engine.started", feeds=self.feeds)

    async def stop(self) -> None:
        """Gracefully shut down all feeds."""
        if self.feeds.get("binance_ws"):
            await self._binance_ws.stop()
        self._running = False
        self.feeds = {}
        logger.info("data_engine.stopped")

    def status(self) -> dict:
        return {
            "service": "data-engine",
            "status": "running" if self._running else "stopped",
            "feeds": self.feeds,
        }


data_engine = DataEngine()
