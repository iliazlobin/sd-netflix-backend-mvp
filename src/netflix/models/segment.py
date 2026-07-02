"""VideoSegment ORM model — mock ABR segment metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netflix.models.title import Title

import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from netflix.models.base import Base, pk_uuid


class VideoSegment(Base):
    __tablename__ = "video_segments"

    segment_id: Mapped[uuid.UUID] = pk_uuid()
    title_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("titles.title_id"), nullable=False
    )
    quality: Mapped[str] = mapped_column(String(10), nullable=False)
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[Title] = relationship("Title", back_populates="segments")

    __table_args__ = (
        UniqueConstraint(
            "title_id",
            "quality",
            "segment_index",
            name="uq_segment_title_quality_index",
        ),
    )
