"""Playback heartbeat request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class HeartbeatRequest(BaseModel):
    """Request body for POST /api/v1/playback/heartbeat."""

    profile_id: uuid.UUID
    title_id: uuid.UUID
    position_seconds: int = Field(..., ge=0)


class HeartbeatResponse(BaseModel):
    """Response body for heartbeat endpoint."""

    profile_id: uuid.UUID
    title_id: uuid.UUID
    position_seconds: int
    updated_at: datetime
