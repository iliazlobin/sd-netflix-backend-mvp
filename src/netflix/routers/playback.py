"""Playback router — POST /api/v1/playback/heartbeat."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.database import get_session
from netflix.schemas import HeartbeatRequest, HeartbeatResponse
from netflix.services import PlaybackService

router = APIRouter(prefix="/api/v1/playback", tags=["playback"])


@router.post("/heartbeat")
async def heartbeat(
    body: HeartbeatRequest,
    session: AsyncSession = Depends(get_session),
) -> HeartbeatResponse:
    """Upsert playback progress and record watch history."""
    service = PlaybackService(session)
    try:
        return await service.heartbeat(body)
    except ValueError as e:
        detail = str(e)
        status = 404 if "Profile" in detail or "Title" in detail else 422
        raise HTTPException(status_code=status, detail=detail) from None
