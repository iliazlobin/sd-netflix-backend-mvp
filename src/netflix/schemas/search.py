"""Search request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SearchResult(BaseModel):
    """A single search result."""

    type: str  # "title", "genre", "cast"
    id: str
    display_name: str
    score: float


class SearchResponse(BaseModel):
    """Response body for GET /api/v1/search."""

    results: list[SearchResult]
