"""Search router — GET /api/v1/search."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.database import get_session
from netflix.schemas import SearchResponse
from netflix.services import SearchService

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.get("/search")
async def search(
    q: str = Query(""),
    limit: int = Query(default=20, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
) -> SearchResponse:
    """Full-text search across titles, genres, and cast members."""
    service = SearchService(session)
    results = await service.search(q, limit=limit)
    return SearchResponse(results=results)
