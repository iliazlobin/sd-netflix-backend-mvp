"""Account ORM model — lightweight identity container for profile scoping."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netflix.models.profile import Profile

import uuid

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from netflix.models.base import Base, TimestampMixin, pk_uuid


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    account_id: Mapped[uuid.UUID] = pk_uuid()
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)

    profiles: Mapped[list[Profile]] = relationship(
        "Profile", back_populates="account", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("email", name="uq_accounts_email"),)
