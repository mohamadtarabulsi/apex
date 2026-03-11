"""Data Engine service — manages all market data ingestion pipelines."""

import structlog

logger = structlog.get_logger()


class DataEngine:
    """Manages WebSocket feeds, REST polling, and indicator computation."""

    def __init__(self):
        self.feeds: dict[str, bool] = {}
        self._running = False

    async def start(self) -> None:
        """Initialize data feeds and start ingestion loops."""
        self._running = True
        self.feeds = {
            "binance_ws": False,
            "alpaca_ws": False,
            "kalshi_rest": False,
            "polymarket_rest": False,
        }
        logger.info("data_engine.started", feeds=list(self.feeds.keys()))

    async def stop(self) -> None:
        """Gracefully shut down all feeds."""
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
