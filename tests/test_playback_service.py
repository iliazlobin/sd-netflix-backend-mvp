"""White-box tests — PlaybackService."""

from __future__ import annotations

import uuid

import pytest as pytest

from netflix.schemas import HeartbeatRequest
from netflix.services import PlaybackService

# Need fixtures for account, profile, title since heartbeat depends on them
# These are integration-level tests requiring seeded data


@pytest.mark.asyncio
async def test_heartbeat_unknown_profile(session):
    """Heartbeat with unknown profile raises ValueError."""
    svc = PlaybackService(session)
    with pytest.raises(ValueError, match="Profile not found"):
        await svc.heartbeat(
            HeartbeatRequest(
                profile_id=uuid.uuid4(),
                title_id=uuid.uuid4(),
                position_seconds=30,
            )
        )


@pytest.mark.asyncio
async def test_heartbeat_negative_position_raises():
    """Pydantic validation rejects negative position."""
    with pytest.raises(ValueError):
        HeartbeatRequest(
            profile_id=uuid.uuid4(),
            title_id=uuid.uuid4(),
            position_seconds=-1,
        )
