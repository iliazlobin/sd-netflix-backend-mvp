"""Profile ORM model — per-account profiles with name uniqueness constraint."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netflix.models.account import Account
    from netflix.models.playback import PlaybackProgress, WatchHistory

import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from netflix.models.base import Base, TimestampMixin, pk_uuid


class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"

    profile_id: Mapped[uuid.UUID] = pk_uuid()
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.account_id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_kids: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    account: Mapped[Account] = relationship("Account", back_populates="profiles")
    playback_progress: Mapped[list[PlaybackProgress]] = relationship(
        "PlaybackProgress", back_populates="profile", cascade="all, delete-orphan"
    )
    watch_history: Mapped[list[WatchHistory]] = relationship(
        "WatchHistory", back_populates="profile", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("account_id", "name", name="uq_profile_name_per_account"),)
