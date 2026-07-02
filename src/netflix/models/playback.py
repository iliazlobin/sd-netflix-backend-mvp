"""PlaybackProgress and WatchHistory ORM models — resume position + viewing history."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netflix.models.profile import Profile
    from netflix.models.title import Title

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from netflix.models.base import Base, TimestampMixin, pk_uuid


class PlaybackProgress(Base, TimestampMixin):
    __tablename__ = "playback_progress"

    progress_id: Mapped[uuid.UUID] = pk_uuid()
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.profile_id"), nullable=False
    )
    title_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("titles.title_id"), nullable=False
    )
    position_seconds: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    profile: Mapped[Profile] = relationship("Profile", back_populates="playback_progress")
    title: Mapped[Title] = relationship("Title", back_populates="playback_progress")

    __table_args__ = (UniqueConstraint("profile_id", "title_id", name="uq_progress_profile_title"),)


class WatchHistory(Base):
    __tablename__ = "watch_history"

    history_id: Mapped[uuid.UUID] = pk_uuid()
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.profile_id"), nullable=False
    )
    title_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("titles.title_id"), nullable=False
    )
    watched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    profile: Mapped[Profile] = relationship("Profile", back_populates="watch_history")
    title: Mapped[Title] = relationship("Title", back_populates="watch_history")
