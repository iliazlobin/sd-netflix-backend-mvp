"""GET /healthz — liveness probe."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz():
    """Return 200 when the app is alive."""
    return {"status": "ok"}
