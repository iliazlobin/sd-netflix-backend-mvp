"""PlaybackService — heartbeat upsert + debounced WatchHistory insert."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.models import Profile, Title
from netflix.schemas import HeartbeatRequest, HeartbeatResponse


class PlaybackService:
    """Business logic for playback heartbeat and watch history."""

    DEBOUNCE_SECONDS = 30

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def heartbeat(self, data: HeartbeatRequest) -> HeartbeatResponse:
        """Upsert playback progress and (debounced) insert watch history."""
        # Verify profile and title exist
        profile = await self._session.get(Profile, data.profile_id)
        if profile is None:
            raise ValueError("Profile not found")

        title = await self._session.get(Title, data.title_id)
        if title is None:
            raise ValueError("Title not found")

        # Upsert PlaybackProgress
        stmt = text("""
            INSERT INTO playback_progress
                (progress_id, profile_id, title_id, position_seconds, updated_at)
            VALUES
                (gen_random_uuid(), :profile_id, :title_id, :position_seconds, now())
            ON CONFLICT (profile_id, title_id)
            DO UPDATE SET
                position_seconds = :position_seconds,
                updated_at = now()
            RETURNING updated_at
        """)
        result = await self._session.execute(
            stmt,
            {
                "profile_id": data.profile_id,
                "title_id": data.title_id,
                "position_seconds": data.position_seconds,
            },
        )
        row = result.fetchone()
        updated_at = row[0] if row else datetime.now(UTC)

        # Debounced WatchHistory insert
        await self._maybe_insert_watch_history(data.profile_id, data.title_id)

        return HeartbeatResponse(
            profile_id=data.profile_id,
            title_id=data.title_id,
            position_seconds=data.position_seconds,
            updated_at=updated_at,
        )

    async def _maybe_insert_watch_history(self, profile_id: uuid.UUID, title_id: uuid.UUID) -> None:
        """Insert a WatchHistory row only if the last entry is > 30s old."""
        stmt = text("""
            SELECT watched_at
            FROM watch_history
            WHERE profile_id = :profile_id AND title_id = :title_id
            ORDER BY watched_at DESC
            LIMIT 1
        """)
        result = await self._session.execute(
            stmt,
            {"profile_id": profile_id, "title_id": title_id},
        )
        row = result.fetchone()

        now = datetime.now(UTC)
        if row is not None:
            last_watched = row[0]
            if last_watched.tzinfo is None:
                last_watched = last_watched.replace(tzinfo=UTC)
            if (now - last_watched).total_seconds() < self.DEBOUNCE_SECONDS:
                return  # Skip — too soon

        # Insert new WatchHistory row
        insert_stmt = text("""
            INSERT INTO watch_history (history_id, profile_id, title_id, watched_at)
            VALUES (gen_random_uuid(), :profile_id, :title_id, now())
        """)
        await self._session.execute(
            insert_stmt,
            {"profile_id": profile_id, "title_id": title_id},
        )
