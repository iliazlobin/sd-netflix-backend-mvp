"""Homepage response schemas — catalog rows assembled by CatalogService."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class ContinueWatchingItem(BaseModel):
    """A title in the continue-watching row."""

    title_id: uuid.UUID
    title: str
    poster_url: str
    maturity_rating: str
    position_seconds: int


class TrendingItem(BaseModel):
    """A title in the trending row."""

    title_id: uuid.UUID
    title: str
    poster_url: str
    maturity_rating: str
    trending_score: float


class GenreRowItem(BaseModel):
    """A title within a genre row."""

    title_id: uuid.UUID
    title: str
    poster_url: str
    maturity_rating: str


class GenreRow(BaseModel):
    """A named genre row with its titles."""

    genre_name: str
    titles: list[GenreRowItem]


class HomePageResponse(BaseModel):
    """Response body for GET /api/v1/home."""

    continue_watching: list[ContinueWatchingItem]
    trending: list[TrendingItem]
    genre_rows: list[GenreRow]
