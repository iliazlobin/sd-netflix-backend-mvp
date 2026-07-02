"""CastMember and TitleCast ORM models — many-to-many with FTS support."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netflix.models.cast import CastMember
    from netflix.models.title import Title

import uuid

from sqlalchemy import Computed, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from netflix.models.base import Base, pk_uuid


class CastMember(Base):
    __tablename__ = "cast_members"

    cast_id: Mapped[uuid.UUID] = pk_uuid()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    fts_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', coalesce(name, ''))",
            persisted=True,
        ),
        nullable=True,
    )

    titles: Mapped[list[TitleCast]] = relationship(
        "TitleCast", back_populates="cast_member", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_cast_members_fts_vector", "fts_vector", postgresql_using="gin"),)


class TitleCast(Base):
    __tablename__ = "title_cast"

    title_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("titles.title_id"),
        primary_key=True,
    )
    cast_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cast_members.cast_id"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)

    title: Mapped[Title] = relationship("Title", back_populates="cast")
    cast_member: Mapped[CastMember] = relationship("CastMember", back_populates="titles")

    __table_args__ = (UniqueConstraint("title_id", "cast_id", "role", name="uq_title_cast_role"),)
