"""Pydantic models for all context schema tables — used for API serialization."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PriceRecord(BaseModel):
    id: int | None = None
    symbol: str
    asset_class: str
    exchange: str | None = None
    timestamp: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    timeframe: str | None = None
    indicators: dict | None = None
    created_at: datetime | None = None


class SentimentRecord(BaseModel):
    id: int | None = None
    symbol: str
    source: str
    model: str | None = None
    score: float
    magnitude: float | None = None
    headline: str | None = None
    reasoning: str | None = None
    timestamp: datetime
    created_at: datetime | None = None


class RegimeRecord(BaseModel):
    id: int | None = None
    scope: str
    state: str
    confidence: float | None = None
    hmm_params: dict | None = None
    timestamp: datetime
    created_at: datetime | None = None


class SignalRecord(BaseModel):
    id: int | None = None
    signal_id: UUID | None = None
    symbol: str
    asset_class: str
    strategy: str
    direction: str
    confidence: float
    risk_reward: float | None = None
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    reasoning: str | None = None
    regime_state: str | None = None
    factors: dict | None = None
    status: str = "pending"
    timestamp: datetime
    created_at: datetime | None = None


class RiskStateRecord(BaseModel):
    id: int | None = None
    portfolio_heat: float | None = None
    var_95: float | None = None
    cvar_95: float | None = None
    current_drawdown: float | None = None
    max_drawdown: float | None = None
    realized_vol: float | None = None
    target_vol: float | None = None
    leverage: float | None = None
    open_positions: int | None = None
    daily_pnl: float | None = None
    weekly_pnl: float | None = None
    risk_limits: dict | None = None
    timestamp: datetime
    created_at: datetime | None = None


class TradeRecord(BaseModel):
    id: int | None = None
    trade_id: UUID | None = None
    signal_id: UUID | None = None
    symbol: str
    asset_class: str
    broker: str
    direction: str
    quantity: float
    entry_price: float | None = None
    exit_price: float | None = None
    pnl: float | None = None
    pnl_pct: float | None = None
    fees: float | None = None
    slippage: float | None = None
    signal_time: datetime | None = None
    order_time: datetime | None = None
    fill_time: datetime | None = None
    exit_time: datetime | None = None
    status: str = "open"
    strategy: str | None = None
    reasoning: str | None = None
    metadata: dict | None = None
    created_at: datetime | None = None


class CalibrationRecord(BaseModel):
    id: int | None = None
    model_name: str
    asset_class: str
    metric_type: str
    metric_value: float
    bucket: str | None = None
    category: str | None = None
    sample_size: int | None = None
    details: dict | None = None
    timestamp: datetime
    created_at: datetime | None = None


class PredictionRecord(BaseModel):
    id: int | None = None
    prediction_id: UUID | None = None
    platform: str
    contract_id: str
    contract_title: str
    category: str | None = None
    market_price: float | None = None
    model_price: float | None = None
    edge: float | None = None
    confidence: float | None = None
    models_used: dict | None = None
    reasoning: str | None = None
    resolution_date: datetime | None = None
    resolved: bool = False
    outcome: bool | None = None
    timestamp: datetime
    created_at: datetime | None = None


class HealthStatus(BaseModel):
    service: str
    status: str
    details: dict = Field(default_factory=dict)


class SystemHealth(BaseModel):
    status: str
    uptime_seconds: float
    services: dict[str, HealthStatus]
