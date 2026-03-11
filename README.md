# APEX — AI-Powered Quantitative Trading System

Personal AI quantitative trading system combining multi-model intelligence, prediction market strategies, and automated execution across crypto, equities, options, and prediction markets.

## Architecture

2-container architecture: a single Python backend monolith + a React dashboard, backed by shared infrastructure.

```
              ┌─────────────────────────────┐
              │       APEX Dashboard        │
              │    React + Tailwind + WS    │
              │       (port 5173)           │
              └─────────────┬───────────────┘
                            │
              ┌─────────────▼───────────────┐
              │      Backend Monolith       │
              │    FastAPI — single process  │
              │       (port 8000)           │
              │                             │
              │  ┌──────────┐ ┌───────────┐ │
              │  │  Data    │ │Intelligence│ │
              │  │  Engine  │ │  Engine    │ │
              │  └──────────┘ └───────────┘ │
              │  ┌──────────┐ ┌───────────┐ │
              │  │ Strategy │ │   Risk &  │ │
              │  │  Engine  │ │ Execution │ │
              │  └──────────┘ └───────────┘ │
              └──┬──────┬──────┬──────┬─────┘
                 │      │      │      │
              ┌──▼──────▼──────▼──────▼─────┐
              │     Shared Context Bus       │
              │ PostgreSQL│QuestDB│Redis│NATS│
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
docker compose up
```

The dashboard will be at `http://localhost:5173` and the API at `http://localhost:8000`.

## Containers

| Container | Port | Description |
|-----------|------|-------------|
| **backend** | 8000 | FastAPI monolith — all 4 modules in one process (REST + WebSocket) |
| **dashboard** | 5173 | React dark terminal UI — real-time trading dashboard |
| **postgres** | 5432 | PostgreSQL 16 — shared context bus (8 tables for signals, trades, risk, calibration) |
| **questdb** | 9000/9009 | QuestDB 9.3.3 — high-frequency tick data and candles (ASOF JOIN, HORIZON JOIN) |
| **redis** | 6379 | Redis 7 — pub/sub, streams, and feature caching |
| **nats** | 4222 | NATS 2.12 JetStream — inter-module event bus |

## API Routes

All endpoints are served by module routers with clear prefixes:

| Module | Prefix | Endpoints |
|--------|--------|-----------|
| Data Engine | `/api/v1/data` | `GET /prices/{symbol}` |
| Intelligence | `/api/v1/intelligence` | `GET /calibration` |
| Strategy | `/api/v1/strategy` | `GET /signals`, `GET /signals/{id}`, `GET /predictions` |
| Risk & Execution | `/api/v1/risk` | `GET /state`, `GET /portfolio` |
| System | `/` | `GET /health`, `GET /api/v1/status`, `WS /ws/feed` |

## Backend Modules

The backend is a single FastAPI process with 4 importable Python packages:

- **data_engine** — Market data ingestion (feeds, indicators)
- **intelligence** — AI/ML model orchestration (sentiment, regime, research agents)
- **strategy** — Trade signal generation (crypto, equities, options, prediction markets)
- **risk_execution** — Risk management and order execution (VaR/CVaR, brokers, kill switch)

All modules share in-process memory via the `shared/` package (config, database, Redis, NATS, QuestDB).

## Tech Stack

- **Backend**: Python 3.12, FastAPI, asyncpg, SQLAlchemy 2.0, NATS JetStream
- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite, Zustand, Lightweight Charts
- **Infrastructure**: PostgreSQL 16, QuestDB 9.3.3, Redis 7, NATS 2.12 JetStream
- **AI/ML**: Claude, GPT, Grok, DeepSeek, Sonar, FinBERT (Phase 3+)
- **Brokers**: Alpaca, Kalshi, Polymarket (Phase 5+)

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
docker compose up postgres questdb redis nats

# Run backend locally
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Run dashboard locally
cd dashboard && npm install && npm run dev
```

## Master Plan

Full system design: [APEX Master Plan v5.3](./docs/APEX_Master_Plan_v5.3.md)
