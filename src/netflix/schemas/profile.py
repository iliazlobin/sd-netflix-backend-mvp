"""Profile CRUD request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProfileCreateRequest(BaseModel):
    """Request body for POST /api/v1/profiles."""

    account_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=100)
    avatar_url: str | None = None
    is_kids: bool = False


class ProfileCreate(BaseModel):
    """Internal create model."""

    account_id: uuid.UUID
    name: str
    avatar_url: str | None = None
    is_kids: bool = False


class ProfileUpdate(BaseModel):
    """Request body for PUT /api/v1/profiles/{profile_id}."""

    name: str | None = Field(None, min_length=1, max_length=100)
    avatar_url: str | None = None
    is_kids: bool | None = None


class ProfileResponse(BaseModel):
    """Response body for profile endpoints."""

    profile_id: uuid.UUID
    account_id: uuid.UUID
    name: str
    avatar_url: str | None
    is_kids: bool
    created_at: datetime
