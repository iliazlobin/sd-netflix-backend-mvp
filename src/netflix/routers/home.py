"""Home router — GET /api/v1/home."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.database import get_session
from netflix.schemas import HomePageResponse
from netflix.services import CatalogService

router = APIRouter(prefix="/api/v1", tags=["home"])


@router.get("/home")
async def get_home(
    profile_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_session),
) -> HomePageResponse:
    """Return the catalog homepage for a profile."""
    service = CatalogService(session)
    try:
        return await service.get_homepage(profile_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
