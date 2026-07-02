"""Streaming router — manifest XML and segment bytes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.database import get_session
from netflix.services import StreamingService

router = APIRouter(prefix="/api/v1", tags=["streaming"])


@router.get("/titles/{title_id}/manifest")
async def get_manifest(
    title_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Return DASH manifest XML for a title."""
    service = StreamingService(session)
    manifest = await service.get_manifest(title_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail="Title has no segments")
    return Response(
        content=manifest,
        media_type="application/dash+xml",
    )


@router.get("/segments/{segment_id}")
async def get_segment(
    segment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Return raw video bytes for a mock segment."""
    service = StreamingService(session)
    result = await service.get_segment(segment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    data, content_type = result
    return Response(content=data, media_type=content_type)
