# APEX — AI-Powered Quantitative Trading System

Personal AI quantitative trading system combining multi-model intelligence, prediction market strategies, and automated execution across crypto, equities, options, and prediction markets.

## Architecture

```
                        ┌─────────────────────────────┐
                        │       APEX Dashboard        │
                        │    React + Tailwind + WS    │
                        │       (port 5173)           │
                        └─────────────┬───────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │        FastAPI Gateway       │
                        │    REST + WebSocket API      │
                        │       (port 8000)           │
                        └──┬──────┬──────┬──────┬─────┘
                           │      │      │      │
              ┌────────────▼┐ ┌───▼──────▼┐ ┌──▼───────────┐
              │ Data Engine  │ │Intelligence│ │   Strategy   │
              │  Feeds +     │ │ AI/ML +    │ │ Signal Gen + │
              │  Indicators  │ │ Agents     │ │ Pred Markets │
              └──────────────┘ └───────────┘ └──────────────┘
                           │      │      │      │
              ┌────────────▼──────▼──────▼──────▼─────┐
              │        Shared Context Bus              │
              │  PostgreSQL │ QuestDB │ Redis │ NATS   │
              └────────────────────────────────────────┘
                                      │
                        ┌─────────────▼───────────────┐
                        │    Risk & Execution Engine   │
                        │  VaR/CVaR + Kill Switch +    │
                        │  Alpaca/Kalshi/Polymarket    │
                        └─────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone
git clone git@github.com:mohamadtarabulsi/apex.git
cd apex

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Launch
docker-compose up
```

The dashboard will be at `http://localhost:5173` and the API at `http://localhost:8000`.

## Services

| Service | Port | Description |
|---------|------|-------------|
| **Dashboard** | 5173 | React dark terminal UI — real-time trading dashboard |
| **API** | 8000 | FastAPI backend — REST + WebSocket gateway |
| **PostgreSQL** | 5432 | Shared context bus — 8 tables for prices, signals, trades, risk |
| **QuestDB** | 9000/9009 | High-frequency time-series — tick data and candles |
| **Redis** | 6379 | Pub/sub, streams, and caching |
| **NATS** | 4222 | JetStream event bus — inter-service messaging |

## Tech Stack

- **Backend**: Python 3.11, FastAPI, asyncpg, SQLAlchemy 2.0, NATS JetStream
- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite, Zustand, Lightweight Charts
- **Infrastructure**: PostgreSQL 16, QuestDB, Redis 7, NATS 2.10
- **AI/ML**: Claude, GPT-4, Grok, DeepSeek, Sonar, FinBERT (Phase 2+)
- **Brokers**: Alpaca, Kalshi, Polymarket (Phase 2+)

## Context Schema

All shared state lives in PostgreSQL under the `context` schema:

1. `context.prices` — OHLCV data with technical indicators
2. `context.sentiment` — AI-generated sentiment scores
3. `context.regime` — HMM regime detection output
4. `context.signals` — Trade signals from all strategies
5. `context.risk_state` — Portfolio-level risk metrics
6. `context.trades` — Executed trade records with TCA
7. `context.calibration` — Model performance tracking
8. `context.predictions` — Prediction market probability estimates

## Development

```bash
# Run just infrastructure
docker-compose up postgres questdb redis nats

# Run API locally
pip install -r requirements.txt
uvicorn api:app --reload --port 8000

# Run dashboard locally
cd dashboard && npm install && npm run dev
```

## Master Plan

Full system design: [APEX Master Plan v5.2](./docs/APEX_Master_Plan_v5.2.md) (placeholder)
