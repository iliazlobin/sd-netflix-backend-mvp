# Netflix MVP — Deployment Guide

> **Slug:** `netflix` · **Stack:** FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL 16 + Alembic

## Prerequisites

- Docker & Docker Compose (or Docker Desktop with Compose plugin)
- Port **8010** (default, override via `APP_PORT`) available on the host
- `curl` for health checks

## From Clean Checkout to Running

```bash
# 1. Clone and enter
git clone <repo-url> sd-netflix-backend-mvp
cd sd-netflix-backend-mvp

# 2. (Optional) Create .env for non-default settings
cp .env.example .env

# 3. Build and start the stack
APP_PORT=8050 docker compose up -d --build

# 4. Wait for health check (15–45s on first run; migrations run on startup)
sleep 15
curl -sf http://localhost:8050/healthz
# Expected: {"status": "ok"}

# 5. Smoke test — create an account
curl -X POST http://localhost:8050/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@test.com"}'

# 6. View logs
docker compose logs app --tail=50
```

## Health Checks

| Service | Endpoint / Command | Expected |
|---------|-------------------|----------|
| `app` | `curl -sf http://localhost:$APP_PORT/healthz` | `{"status": "ok"}` |
| `db` | `docker compose exec db pg_isready -U netflix` | `accepting connections` |

## Running Tests

### Acceptance tests (black-box, require running stack)

```bash
pip install httpx pytest
API_BASE_URL=http://localhost:8050 python -m pytest verify/acceptance -q -v
```

### Unit tests (white-box, standalone)

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q -v
```

### Lint

```bash
pip install ruff
ruff check src/ tests/ verify/
ruff format src/ tests/ verify/ --check
```

## Teardown

```bash
APP_PORT=8050 docker compose down --volumes --remove-orphans
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_PORT` | `8010` | Host port mapped to app container |
| `DATABASE_URL` | `postgresql+asyncpg://netflix:netflix@db:5432/netflix` | Asyncpg connection string |
| `HOST` | `0.0.0.0` | App bind address (inside container) |
| `PORT` | `8000` | App listen port (inside container) |
| `LOG_LEVEL` | `INFO` | Log verbosity |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `MOCK_SEGMENTS_DIR` | `/app/data/segments` | Mock .ts segment directory |

## CI/CD Workflows

| Workflow | Trigger | What it does |
|----------|---------|-------------|
| `lint.yml` | PRs to `main` | Ruff check + format check |
| `ci.yml` | PRs to `main` | Postgres service, unit tests, build |
| `functional.yml` | Push to `main` | Full compose stack, migrations, acceptance tests |

## Port Collision Note

Postgres port 5432 is **not** published to the host — the app connects over the internal compose network. To inspect the database from the host:

```bash
docker compose exec db psql -U netflix -d netflix
```

## Production Notes

- Replace `CORS_ORIGINS=*` with specific origins before deploying publicly.
- Pin Postgres image version tag in production (`postgres:16-alpine` is already version-pinned).
- Set `LOG_LEVEL=WARNING` or `ERROR` in production to reduce noise.
- The app runs as a non-root user inside the container.
