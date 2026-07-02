"""Account request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class AccountCreateRequest(BaseModel):
    """Request body for POST /api/v1/accounts."""

    email: str


class AccountCreate(BaseModel):
    """Internal create request with validated/normalized fields."""

    email: str


class AccountResponse(BaseModel):
    """Response body for account endpoints."""

    account_id: uuid.UUID
    email: str
    created_at: datetime
