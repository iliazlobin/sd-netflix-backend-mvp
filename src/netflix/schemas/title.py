"""Title detail response schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class CastMemberOut(BaseModel):
    """Cast member in a title detail response."""

    cast_id: uuid.UUID
    name: str
    role: str


class GenreOut(BaseModel):
    """Genre in a title detail response."""

    genre_id: uuid.UUID
    name: str


class TitleDetailResponse(BaseModel):
    """Response body for GET /api/v1/titles/{title_id}."""

    title_id: uuid.UUID
    title: str
    synopsis: str
    release_year: int
    maturity_rating: str
    poster_url: str
    backdrop_url: str
    title_type: str
    trending_score: float
    cast: list[CastMemberOut]
    genres: list[GenreOut]


class TitleListItem(BaseModel):
    """A title in a list context (homepage rows, search results)."""

    title_id: uuid.UUID
    title: str
    poster_url: str
    maturity_rating: str
