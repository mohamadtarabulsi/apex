"""Strategy Engine — generates trade signals from context bus data."""

import structlog

logger = structlog.get_logger()


class StrategyEngine:
    """Runs all active trading strategies and emits signals."""

    def __init__(self):
        self.strategies: dict[str, bool] = {}
        self._running = False

    async def start(self) -> None:
        """Initialize and register all active strategies."""
        self._running = True
        self.strategies = {
            "weather_bot": False,
            "crypto_momentum": False,
            "prediction_arb": False,
        }
        logger.info("strategy_engine.started", strategies=list(self.strategies.keys()))

    async def stop(self) -> None:
        self._running = False
        self.strategies = {}
        logger.info("strategy_engine.stopped")

    def status(self) -> dict:
        return {
            "service": "strategy",
            "status": "running" if self._running else "stopped",
            "strategies": self.strategies,
        }


strategy_engine = StrategyEngine()
