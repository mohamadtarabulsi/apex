# APEX — Project Instructions

## Overview
APEX is a personal AI quantitative trading system. 2-container architecture: Python backend monolith + React dashboard.

## Architecture
- **Backend**: Python 3.12 FastAPI monolith — 4 modules (data_engine, intelligence, strategy, risk_execution) in one process
- **Dashboard**: React 18 + TypeScript + Vite + Tailwind CSS — dark terminal aesthetic
- **Infrastructure**: PostgreSQL 16 + QuestDB 9.3.3 + Redis 7 + NATS 2.12 JetStream
- **Deployment**: `docker compose up` — 2 app containers + 4 infra containers

## Repository Structure
```
backend/
  main.py              # FastAPI app — imports all 4 modules
  data_engine/         # Service 1: market data ingestion
  intelligence/        # Service 2: AI/ML inference
  strategy/            # Service 3: trading strategies
  risk_execution/      # Service 4: risk mgmt + order execution
  shared/              # Shared utilities (config, DB, Redis, NATS, QuestDB)
dashboard/
  src/
    components/        # React components
    hooks/             # Custom hooks (useWebSocket)
    stores/            # Zustand state management
    types/             # TypeScript type definitions
    lib/               # API client helpers
docker/
  postgres/init.sql    # PostgreSQL schema initialization
```

## Code Conventions

### Python (backend/)
- Python 3.12, type hints everywhere
- FastAPI with async/await, asyncpg for PostgreSQL
- Use `datetime.now(timezone.utc)` — never `datetime.utcnow()` (deprecated)
- Structured logging via `structlog`
- Each module has: `engine.py` (core logic), `router.py` (FastAPI endpoints), `__init__.py` (exports)
- Shared state via PostgreSQL `context` schema (8 tables) — not in-memory globals
- Environment config via Pydantic settings from `.env`

### TypeScript (dashboard/)
- React 18, strict TypeScript, functional components only
- Zustand for global state — single store in `stores/appStore.ts`
- Single WebSocket connection in `useWebSocket.ts` — components read from the store, never open their own connections
- Tailwind CSS with custom APEX theme (bg: #0a0a0f, green: #00ff88, blue: #0088ff, red: #ff3366)
- JetBrains Mono font throughout

### API
- Module routers with prefixes: `/api/v1/data`, `/api/v1/intelligence`, `/api/v1/strategy`, `/api/v1/risk`
- System endpoints: `GET /health`, `GET /api/v1/status`, `WS /ws/feed`
- No duplicate endpoints — each endpoint lives in exactly one router

### Infrastructure
- Docker Compose — no `version:` key (deprecated)
- PostgreSQL schema auto-created via `docker/postgres/init.sql`
- All service connections initialized on FastAPI startup via lifespan context manager

## Commit Style
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- Push directly to `main` for now (single developer)
