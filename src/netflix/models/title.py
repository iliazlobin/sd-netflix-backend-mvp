"""Title ORM model — catalog entries with full-text search support."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netflix.models.cast import TitleCast
    from netflix.models.genre import TitleGenre
    from netflix.models.playback import PlaybackProgress, WatchHistory
    from netflix.models.segment import VideoSegment

import uuid

from sqlalchemy import (
    CheckConstraint,
    Computed,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from netflix.models.base import Base, TimestampMixin, pk_uuid


class Title(Base, TimestampMixin):
    __tablename__ = "titles"

    title_id: Mapped[uuid.UUID] = pk_uuid()
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    synopsis: Mapped[str] = mapped_column(Text, nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    maturity_rating: Mapped[str] = mapped_column(String(10), nullable=False)
    poster_url: Mapped[str] = mapped_column(String(500), nullable=False)
    backdrop_url: Mapped[str] = mapped_column(String(500), nullable=False)
    title_type: Mapped[str] = mapped_column(String(20), nullable=False)
    trending_score: Mapped[float] = mapped_column(Float, server_default="0.0", nullable=False)
    fts_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(synopsis, ''))",
            persisted=True,
        ),
        nullable=True,
    )

    genres: Mapped[list[TitleGenre]] = relationship(
        "TitleGenre", back_populates="title", cascade="all, delete-orphan"
    )
    cast: Mapped[list[TitleCast]] = relationship(
        "TitleCast", back_populates="title", cascade="all, delete-orphan"
    )
    playback_progress: Mapped[list[PlaybackProgress]] = relationship(
        "PlaybackProgress", back_populates="title", cascade="all, delete-orphan"
    )
    watch_history: Mapped[list[WatchHistory]] = relationship(
        "WatchHistory", back_populates="title", cascade="all, delete-orphan"
    )
    segments: Mapped[list[VideoSegment]] = relationship(
        "VideoSegment", back_populates="title", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_titles_fts_vector", "fts_vector", postgresql_using="gin"),
        Index("ix_titles_trending_score", "trending_score", postgresql_using="btree"),
        CheckConstraint(
            "release_year >= 1888",
            name="ck_titles_release_year",
        ),
    )
