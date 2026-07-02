"""TitleService — title detail with cast and genres."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from netflix.models import Title, TitleCast, TitleGenre
from netflix.schemas import CastMemberOut, GenreOut, TitleDetailResponse


class TitleService:
    """Business logic for title detail."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_title_detail(self, title_id: uuid.UUID) -> TitleDetailResponse | None:
        """Fetch a title with cast and genres eagerly loaded."""
        stmt = (
            select(Title)
            .where(Title.title_id == title_id)
            .options(
                selectinload(Title.cast).selectinload(TitleCast.cast_member),
                selectinload(Title.genres).selectinload(TitleGenre.genre),
            )
        )
        result = await self._session.execute(stmt)
        title = result.scalar_one_or_none()
        if title is None:
            return None

        return TitleDetailResponse(
            title_id=title.title_id,
            title=title.title,
            synopsis=title.synopsis,
            release_year=title.release_year,
            maturity_rating=title.maturity_rating,
            poster_url=title.poster_url,
            backdrop_url=title.backdrop_url,
            title_type=title.title_type,
            trending_score=title.trending_score,
            cast=[
                CastMemberOut(
                    cast_id=tc.cast_member.cast_id,
                    name=tc.cast_member.name,
                    role=tc.role,
                )
                for tc in title.cast
            ],
            genres=[
                GenreOut(
                    genre_id=tg.genre.genre_id,
                    name=tg.genre.name,
                )
                for tg in title.genres
            ],
        )
