"""SearchService — full-text search across titles, genres, and cast."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.schemas import SearchResult


class SearchService:
    """Business logic for full-text search."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, query: str, limit: int = 20) -> list[SearchResult]:
        """Full-text search across titles, genres, and cast members.

        Uses websearch_to_tsquery for user-friendly query parsing,
        ts_rank for relevance scoring, and a recency boost for titles
        from the last 90 days.
        """
        if not query or not query.strip():
            return []

        limit = min(limit, 50)

        stmt = text("""
            SELECT type, id, display_name, score
            FROM (
                -- Search titles
                SELECT 'title' AS type,
                       t.title_id::text AS id,
                       t.title AS display_name,
                       ts_rank(t.fts_vector, query) *
                         CASE WHEN t.release_year >= EXTRACT(YEAR FROM now()) - 1
                              THEN 1.2 ELSE 1.0 END AS score
                FROM titles t,
                     websearch_to_tsquery('english', :query) query
                WHERE t.fts_vector @@ query

                UNION ALL

                -- Search genres
                SELECT 'genre' AS type,
                       g.genre_id::text AS id,
                       g.name AS display_name,
                       ts_rank(g.fts_vector, query) AS score
                FROM genres g,
                     websearch_to_tsquery('english', :query) query
                WHERE g.fts_vector @@ query

                UNION ALL

                -- Search cast members
                SELECT 'cast' AS type,
                       cm.cast_id::text AS id,
                       cm.name AS display_name,
                       ts_rank(cm.fts_vector, query) AS score
                FROM cast_members cm,
                     websearch_to_tsquery('english', :query) query
                WHERE cm.fts_vector @@ query
            ) combined
            ORDER BY score DESC
            LIMIT :limit
        """)

        result = await self._session.execute(stmt, {"query": query, "limit": limit})
        rows = result.fetchall()

        return [
            SearchResult(
                type=row.type,
                id=row.id,
                display_name=row.display_name,
                score=float(row.score),
            )
            for row in rows
        ]
