# syntax=docker/dockerfile:1
# Multi-stage build: builder → runtime (python:3.12-slim)

# ---- Builder stage ----
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build deps (none needed for pure Python pkgs, but keep uv)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim

WORKDIR /app

# Python tuning
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app/src

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ /app/src/
COPY alembic.ini /app/alembic.ini
COPY alembic/ /app/alembic/

# Copy mock segment files
COPY data/segments/ /app/data/segments/

# Runs as root so the console scripts installed under /root/.local/bin (alembic, uvicorn)
# are executable — a non-root user cannot traverse root's home to reach them.
# Alembic auto-upgrade on startup, then start uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn netflix.main:app --host 0.0.0.0 --port 8000"]
