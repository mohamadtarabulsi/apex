"""Event types and NATS subject definitions for the APEX event bus."""

from enum import Enum


class Subject(str, Enum):
    """NATS subject hierarchy for inter-service communication."""

    # Price events
    PRICE_TICK = "prices.tick.{symbol}"
    PRICE_CANDLE = "prices.candle.{symbol}.{timeframe}"
    PRICE_INDICATOR = "prices.indicator.{symbol}"

    # Signal events
    SIGNAL_NEW = "signals.new.{strategy}"
    SIGNAL_APPROVED = "signals.approved.{signal_id}"
    SIGNAL_REJECTED = "signals.rejected.{signal_id}"
    SIGNAL_EXECUTED = "signals.executed.{signal_id}"

    # Risk events
    RISK_UPDATE = "risk.update"
    RISK_ALERT = "risk.alert.{level}"
    RISK_KILL_SWITCH = "risk.kill_switch"

    # System events
    EVENT_SERVICE_UP = "events.service.up.{service}"
    EVENT_SERVICE_DOWN = "events.service.down.{service}"
    EVENT_HEALTH = "events.health"

    def format(self, **kwargs) -> str:
        """Format subject with dynamic parts."""
        return self.value.format(**kwargs)


class EventType(str, Enum):
    """Event payload type identifiers."""

    TICK = "tick"
    CANDLE = "candle"
    INDICATOR = "indicator"
    SIGNAL = "signal"
    TRADE = "trade"
    RISK_UPDATE = "risk_update"
    RISK_ALERT = "risk_alert"
    SERVICE_STATUS = "service_status"
    HEALTH_CHECK = "health_check"
