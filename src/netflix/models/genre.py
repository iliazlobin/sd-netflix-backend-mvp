"""Genre and TitleGenre ORM models — many-to-many with FTS support."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netflix.models.genre import Genre
    from netflix.models.title import Title

import uuid

from sqlalchemy import Computed, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from netflix.models.base import Base, pk_uuid


class Genre(Base):
    __tablename__ = "genres"

    genre_id: Mapped[uuid.UUID] = pk_uuid()
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    fts_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', coalesce(name, ''))",
            persisted=True,
        ),
        nullable=True,
    )

    titles: Mapped[list[TitleGenre]] = relationship(
        "TitleGenre", back_populates="genre", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_genres_fts_vector", "fts_vector", postgresql_using="gin"),)


class TitleGenre(Base):
    __tablename__ = "title_genres"

    title_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("titles.title_id"),
        primary_key=True,
    )
    genre_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("genres.genre_id"),
        primary_key=True,
    )

    title: Mapped[Title] = relationship("Title", back_populates="genres")
    genre: Mapped[Genre] = relationship("Genre", back_populates="titles")

    __table_args__ = (UniqueConstraint("title_id", "genre_id", name="uq_title_genre"),)
