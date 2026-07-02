# Netflix MVP — Deployment Guide

## Prerequisites

- Docker & Docker Compose (or Docker Desktop with Compose plugin)
- Port 8050 (or `APP_PORT` override) available on the host

## First Run

```bash
# 1. Build and start
APP_PORT=8050 docker compose up -d --build

# 2. Wait for health check to pass (30–60s on first run)
curl http://localhost:8050/healthz
# → {"status": "ok"}

# 3. Migrations run automatically on startup (alembic upgrade head).
#    Seed data is pre-loaded: 1 account, 3 profiles, ~30 titles
#    across 6 genres, cast members, and mock video segments.

# 4. Smoke test — create an account
curl -X POST http://localhost:8050/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@test.com"}'

# 5. View logs
docker compose logs app --tail=50
```

## Running Tests

```bash
# Black-box acceptance tests (against the running stack)
pip install httpx pytest
API_BASE_URL=http://localhost:8050 pytest verify/acceptance -q -v

# White-box unit tests (standalone, no Docker needed if Postgres available)
pip install -e ".[dev]"
pytest tests/ -q -v
```

## Teardown

```bash
APP_PORT=8050 docker compose down --volumes --remove-orphans
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_PORT` | `8010` | Host port mapped to the app container (port 8000 inside) |
| `DATABASE_URL` | `postgresql+asyncpg://netflix:netflix@db:5432/netflix` | Postgres connection string |
| `LOG_LEVEL` | `INFO` | Log verbosity (DEBUG, INFO, WARNING, ERROR) |
| `CORS_ORIGINS` | `*` | Comma-separated allowed CORS origins |
| `MOCK_SEGMENTS_DIR` | `/app/data/segments` | Directory containing mock .ts files |

## Port Collision Note

The compose file does **not** publish Postgres port 5432 to the host. Publishing it would collide with any Postgres already running on the host (common during local development). The app connects to the database over the internal compose network. If you need to inspect the database from the host, use:

```bash
docker compose exec db psql -U netflix -d netflix
```
