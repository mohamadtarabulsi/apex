"""NATS JetStream client for inter-service event bus."""

import nats
from nats.aio.client import Client as NATSClient
from nats.js.api import StreamConfig
import structlog

from shared.config import settings

logger = structlog.get_logger()

_nc: NATSClient | None = None


async def get_nats() -> NATSClient:
    """Get or create the NATS connection."""
    global _nc
    if _nc is None or _nc.is_closed:
        _nc = await nats.connect(settings.nats_url)
        # Ensure JetStream streams exist
        js = _nc.jetstream()
        streams = [
            StreamConfig(name="SIGNALS", subjects=["signals.>"], max_msgs=10000),
            StreamConfig(name="PRICES", subjects=["prices.>"], max_msgs=100000),
            StreamConfig(name="RISK", subjects=["risk.>"], max_msgs=10000),
            StreamConfig(name="EVENTS", subjects=["events.>"], max_msgs=50000),
        ]
        for cfg in streams:
            try:
                await js.add_stream(cfg)
                logger.info("NATS stream created", stream=cfg.name)
            except Exception:
                # Stream may already exist
                await js.update_stream(cfg)
                logger.info("NATS stream updated", stream=cfg.name)
        logger.info("NATS connected", url=settings.nats_url)
    return _nc


async def close_nats() -> None:
    """Close the NATS connection."""
    global _nc
    if _nc is not None and not _nc.is_closed:
        await _nc.drain()
        _nc = None
        logger.info("NATS connection closed")


async def check_nats() -> dict:
    """Health check — verify connection."""
    try:
        nc = await get_nats()
        if nc.is_connected:
            return {"status": "healthy", "server": str(nc.connected_url)}
        return {"status": "unhealthy", "reason": "not connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
