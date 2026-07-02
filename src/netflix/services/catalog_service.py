"""CatalogService — homepage row assembly (continue-watching, trending, genre rows)."""

from __future__ import annotations

import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.models import Profile, Title
from netflix.schemas import (
    ContinueWatchingItem,
    GenreRow,
    GenreRowItem,
    HomePageResponse,
    TrendingItem,
)


class CatalogService:
    """Business logic for the catalog homepage."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_homepage(self, profile_id: uuid.UUID) -> HomePageResponse:
        """Assemble the catalog homepage for a profile."""
        # Verify profile exists
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            raise ValueError("Profile not found")

        continue_watching = await self._get_continue_watching(profile_id)
        trending = await self._get_trending()
        genre_rows = await self._get_genre_rows()

        return HomePageResponse(
            continue_watching=continue_watching,
            trending=trending,
            genre_rows=genre_rows,
        )

    async def _get_continue_watching(self, profile_id: uuid.UUID) -> list[ContinueWatchingItem]:
        """Fetch continue-watching titles (up to 10, most recent first)."""
        stmt = text("""
            SELECT DISTINCT ON (wh.title_id)
                t.title_id, t.title, t.poster_url, t.maturity_rating,
                COALESCE(pp.position_seconds, 0) AS position_seconds,
                wh.watched_at
            FROM watch_history wh
            JOIN titles t ON t.title_id = wh.title_id
            LEFT JOIN playback_progress pp
                ON pp.profile_id = wh.profile_id AND pp.title_id = wh.title_id
            WHERE wh.profile_id = :profile_id
            ORDER BY wh.title_id, wh.watched_at DESC
            LIMIT 10
        """)
        result = await self._session.execute(stmt, {"profile_id": profile_id})
        rows = result.fetchall()
        return [
            ContinueWatchingItem(
                title_id=row.title_id,
                title=row.title,
                poster_url=row.poster_url,
                maturity_rating=row.maturity_rating,
                position_seconds=row.position_seconds,
            )
            for row in rows
        ]

    async def _get_trending(self) -> list[TrendingItem]:
        """Fetch trending titles (up to 20, by trending_score)."""
        stmt = select(Title).order_by(Title.trending_score.desc()).limit(20)
        result = await self._session.execute(stmt)
        titles = result.scalars().all()
        return [
            TrendingItem(
                title_id=t.title_id,
                title=t.title,
                poster_url=t.poster_url,
                maturity_rating=t.maturity_rating,
                trending_score=t.trending_score,
            )
            for t in titles
        ]

    async def _get_genre_rows(self) -> list[GenreRow]:
        """Fetch top 6 genres by title count, 10 titles each."""
        stmt = text("""
            WITH top_genres AS (
                SELECT g.genre_id, g.name, COUNT(*) AS title_count
                FROM genres g
                JOIN title_genres tg ON tg.genre_id = g.genre_id
                GROUP BY g.genre_id, g.name
                ORDER BY title_count DESC
                LIMIT 6
            ),
            genre_titles AS (
                SELECT tg.genre_id, t.title_id, t.title, t.poster_url, t.maturity_rating,
                       ROW_NUMBER() OVER (
                           PARTITION BY tg.genre_id
                           ORDER BY t.trending_score DESC
                       ) AS rn
                FROM title_genres tg
                JOIN titles t ON t.title_id = tg.title_id
                WHERE tg.genre_id IN (SELECT genre_id FROM top_genres)
            )
            SELECT g.name AS genre_name,
                   gt.title_id, gt.title, gt.poster_url, gt.maturity_rating
            FROM top_genres g
            JOIN genre_titles gt ON gt.genre_id = g.genre_id AND gt.rn <= 10
            ORDER BY g.title_count DESC, gt.rn
        """)
        result = await self._session.execute(stmt)
        rows = result.fetchall()

        # Group by genre
        genre_map: dict[str, list[GenreRowItem]] = {}
        for row in rows:
            if row.genre_name not in genre_map:
                genre_map[row.genre_name] = []
            genre_map[row.genre_name].append(
                GenreRowItem(
                    title_id=row.title_id,
                    title=row.title,
                    poster_url=row.poster_url,
                    maturity_rating=row.maturity_rating,
                )
            )

        return [GenreRow(genre_name=name, titles=titles) for name, titles in genre_map.items()]
