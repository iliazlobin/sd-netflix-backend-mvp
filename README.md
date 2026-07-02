# Netflix MVP

An MVP streaming backend — catalog browsing, full-text search, ABR video streaming with mock segments, playback resume via heartbeat, and multi-profile management.

**Stack:** FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL 16 + Alembic + Docker Compose

## Quick Start

```bash
# Start the full stack (app + postgres)
docker compose up -d --build

# Check health
curl http://localhost:8010/healthz
# → {"status": "ok"}

# Run acceptance tests
pip install httpx pytest
API_BASE_URL=http://localhost:8010 pytest verify/acceptance -q
```

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| POST | `/api/v1/accounts` | Create account |
| GET | `/api/v1/accounts/{id}` | Get account |
| GET | `/api/v1/home?profile_id=` | Catalog homepage (continue-watching, trending, genre rows) |
| GET | `/api/v1/titles/{id}` | Title detail with cast and genres |
| GET | `/api/v1/titles/{id}/manifest` | DASH manifest XML |
| GET | `/api/v1/segments/{id}` | Raw video segment bytes |
| POST | `/api/v1/playback/heartbeat` | Upsert playback position |
| GET | `/api/v1/profiles?account_id=` | List profiles |
| POST | `/api/v1/profiles` | Create profile |
| PUT | `/api/v1/profiles/{id}` | Update profile |
| DELETE | `/api/v1/profiles/{id}` | Delete profile + cascade playback data |
| GET | `/api/v1/search?q=&limit=` | Full-text search |

## Project Structure

```
src/netflix/         # Application package (src layout)
├── main.py          # FastAPI app factory + lifespan + /healthz
├── config.py        # pydantic-settings configuration
├── database.py      # Async engine, session factory, get_session dependency
├── models/          # SQLAlchemy ORM models (10 tables)
├── schemas/         # Pydantic request/response DTOs
├── routers/         # HTTP layer (thin — delegates to services)
└── services/        # Business logic + data access
tests/               # White-box unit/integration tests
verify/              # Black-box acceptance tests (per-FR, HTTP-only)
alembic/             # Migrations (001_initial + 002_seed)
docs/                # System design, MVP scope, build synthesis
```

## Environment Variables

See `.env.example` for all configurable settings. Override via docker-compose `environment:` or a local `.env` file.

## Design Decisions

- **Postgres-only** — no Redis cache at MVP scale (sub-1000 titles, sub-100 QPS)
- **Debounced WatchHistory** — heartbeats fire every 5–10s; insert only if last entry is > 30s old
- **Mock segments** — one ~4KB file per quality level; all titles share the same files
- **Account-scoped profile names** — `UNIQUE(account_id, name)` matches Netflix's real constraint
- **Three FTS tsvector columns** — titles, genres, cast_members each have their own GIN-indexed column; search UNIONs across all three
- **No cursor pagination** — homepage is a fixed layout (max ~360 titles), search caps at 50 results
