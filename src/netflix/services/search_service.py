"""SearchService — full-text search across titles, genres, and cast.

Uses PostgreSQL full-text search (FTS) with a LIKE/ILIKE fallback
for stop-word queries ("the", "a", etc.) that FTS would otherwise ignore.
"""

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
        ts_rank for relevance scoring, with substring (ILIKE) fallback
        for stop-word queries that FTS would ignore.
        """
        if not query or not query.strip():
            return []

        limit = min(limit, 50)

        stmt = text("""
            SELECT type, id, display_name, score
            FROM (
                SELECT DISTINCT ON (sq.type, sq.id)
                    sq.type, sq.id, sq.display_name, sq.score
                FROM (
                    -- Search titles via FTS
                    SELECT 'title' AS type,
                           t.title_id::text AS id,
                           t.title AS display_name,
                           ts_rank(t.fts_vector, query) AS score
                    FROM titles t,
                         websearch_to_tsquery('english', :query) query
                    WHERE t.fts_vector @@ query

                    UNION ALL

                    -- Search titles via substring (handles stop words)
                    SELECT 'title' AS type,
                           t.title_id::text AS id,
                           t.title AS display_name,
                           0.01 AS score
                    FROM titles t
                    WHERE t.title ILIKE '%' || :query || '%'

                    UNION ALL

                    -- Search genres via FTS
                    SELECT 'genre' AS type,
                           g.genre_id::text AS id,
                           g.name AS display_name,
                           ts_rank(g.fts_vector, query) AS score
                    FROM genres g,
                         websearch_to_tsquery('english', :query) query
                    WHERE g.fts_vector @@ query

                    UNION ALL

                    -- Search genres via substring
                    SELECT 'genre' AS type,
                           g.genre_id::text AS id,
                           g.name AS display_name,
                           0.01 AS score
                    FROM genres g
                    WHERE g.name ILIKE '%' || :query || '%'

                    UNION ALL

                    -- Search cast members via FTS
                    SELECT 'cast' AS type,
                           cm.cast_id::text AS id,
                           cm.name AS display_name,
                           ts_rank(cm.fts_vector, query) AS score
                    FROM cast_members cm,
                         websearch_to_tsquery('english', :query) query
                    WHERE cm.fts_vector @@ query

                    UNION ALL

                    -- Search cast members via substring
                    SELECT 'cast' AS type,
                           cm.cast_id::text AS id,
                           cm.name AS display_name,
                           0.01 AS score
                    FROM cast_members cm
                    WHERE cm.name ILIKE '%' || :query || '%'
                ) sq
                ORDER BY sq.type, sq.id, sq.score DESC
            ) ranked
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
