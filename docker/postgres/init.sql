-- APEX Phase 1 — Shared Context Bus Schema Initialization
-- This script runs automatically when the PostgreSQL container starts.

CREATE SCHEMA IF NOT EXISTS context;

-- 1. context.prices: OHLCV data
CREATE TABLE context.prices (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    asset_class VARCHAR(16) NOT NULL,
    exchange VARCHAR(32),
    timestamp TIMESTAMPTZ NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    timeframe VARCHAR(8),
    indicators JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_prices_symbol_ts ON context.prices(symbol, timestamp DESC);
CREATE INDEX idx_prices_asset_class ON context.prices(asset_class, timestamp DESC);

-- 2. context.sentiment: AI-generated sentiment scores
CREATE TABLE context.sentiment (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    source VARCHAR(32) NOT NULL,
    model VARCHAR(64),
    score DOUBLE PRECISION NOT NULL,
    magnitude DOUBLE PRECISION,
    headline TEXT,
    reasoning TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_sentiment_symbol_ts ON context.sentiment(symbol, timestamp DESC);

-- 3. context.regime: HMM regime detection output
CREATE TABLE context.regime (
    id BIGSERIAL PRIMARY KEY,
    scope VARCHAR(32) NOT NULL,
    state VARCHAR(16) NOT NULL,
    confidence DOUBLE PRECISION,
    hmm_params JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_regime_scope_ts ON context.regime(scope, timestamp DESC);

-- 4. context.signals: Trade signals from Strategy Engine
CREATE TABLE context.signals (
    id BIGSERIAL PRIMARY KEY,
    signal_id UUID DEFAULT gen_random_uuid(),
    symbol VARCHAR(32) NOT NULL,
    asset_class VARCHAR(16) NOT NULL,
    strategy VARCHAR(64) NOT NULL,
    direction VARCHAR(8) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    risk_reward DOUBLE PRECISION,
    entry_price DOUBLE PRECISION,
    stop_loss DOUBLE PRECISION,
    take_profit DOUBLE PRECISION,
    reasoning TEXT,
    regime_state VARCHAR(16),
    factors JSONB,
    status VARCHAR(16) DEFAULT 'pending',
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_signals_status ON context.signals(status, timestamp DESC);
CREATE INDEX idx_signals_strategy ON context.signals(strategy, timestamp DESC);

-- 5. context.risk_state: Portfolio-level risk metrics
CREATE TABLE context.risk_state (
    id BIGSERIAL PRIMARY KEY,
    portfolio_heat DOUBLE PRECISION,
    var_95 DOUBLE PRECISION,
    cvar_95 DOUBLE PRECISION,
    current_drawdown DOUBLE PRECISION,
    max_drawdown DOUBLE PRECISION,
    realized_vol DOUBLE PRECISION,
    target_vol DOUBLE PRECISION,
    leverage DOUBLE PRECISION,
    open_positions INTEGER,
    daily_pnl DOUBLE PRECISION,
    weekly_pnl DOUBLE PRECISION,
    risk_limits JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_risk_state_ts ON context.risk_state(timestamp DESC);

-- 6. context.trades: All executed trades
CREATE TABLE context.trades (
    id BIGSERIAL PRIMARY KEY,
    trade_id UUID DEFAULT gen_random_uuid(),
    signal_id UUID,
    symbol VARCHAR(32) NOT NULL,
    asset_class VARCHAR(16) NOT NULL,
    broker VARCHAR(16) NOT NULL,
    direction VARCHAR(8) NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    entry_price DOUBLE PRECISION,
    exit_price DOUBLE PRECISION,
    pnl DOUBLE PRECISION,
    pnl_pct DOUBLE PRECISION,
    fees DOUBLE PRECISION,
    slippage DOUBLE PRECISION,
    signal_time TIMESTAMPTZ,
    order_time TIMESTAMPTZ,
    fill_time TIMESTAMPTZ,
    exit_time TIMESTAMPTZ,
    status VARCHAR(16) DEFAULT 'open',
    strategy VARCHAR(64),
    reasoning TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_trades_status ON context.trades(status, created_at DESC);
CREATE INDEX idx_trades_strategy ON context.trades(strategy, created_at DESC);

-- 7. context.calibration: Model performance tracking
CREATE TABLE context.calibration (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(64) NOT NULL,
    asset_class VARCHAR(16) NOT NULL,
    metric_type VARCHAR(32) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    bucket VARCHAR(32),
    category VARCHAR(64),
    sample_size INTEGER,
    details JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_calibration_model ON context.calibration(model_name, timestamp DESC);

-- 8. context.predictions: Prediction market probability estimates
CREATE TABLE context.predictions (
    id BIGSERIAL PRIMARY KEY,
    prediction_id UUID DEFAULT gen_random_uuid(),
    platform VARCHAR(16) NOT NULL,
    contract_id VARCHAR(128) NOT NULL,
    contract_title TEXT NOT NULL,
    category VARCHAR(64),
    market_price DOUBLE PRECISION,
    model_price DOUBLE PRECISION,
    edge DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    models_used JSONB,
    reasoning TEXT,
    resolution_date TIMESTAMPTZ,
    resolved BOOLEAN DEFAULT FALSE,
    outcome BOOLEAN,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_predictions_platform ON context.predictions(platform, resolved, timestamp DESC);
CREATE INDEX idx_predictions_edge ON context.predictions(edge DESC) WHERE resolved = FALSE;
