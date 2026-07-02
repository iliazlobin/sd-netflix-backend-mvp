"""Titles router — GET /api/v1/titles/{title_id}."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.database import get_session
from netflix.schemas import TitleDetailResponse
from netflix.services import TitleService

router = APIRouter(prefix="/api/v1/titles", tags=["titles"])


@router.get("/{title_id}")
async def get_title(
    title_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> TitleDetailResponse:
    """Return title detail with cast and genres."""
    service = TitleService(session)
    title = await service.get_title_detail(title_id)
    if title is None:
        raise HTTPException(status_code=404, detail="Title not found")
    return title
