"""ProfileService — CRUD with account-scoped name uniqueness."""

from __future__ import annotations

import uuid

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.models import Account, Profile
from netflix.schemas import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)


class ProfileService:
    """Business logic for profile CRUD."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_profile(self, data: ProfileCreate) -> ProfileResponse:
        """Create a new profile. Raises ValueError on issues."""
        # Verify account exists
        account = await self._session.get(Account, data.account_id)
        if account is None:
            raise ValueError("Account not found")

        try:
            profile = Profile(
                account_id=data.account_id,
                name=data.name,
                avatar_url=data.avatar_url,
                is_kids=data.is_kids,
            )
            self._session.add(profile)
            await self._session.flush()
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise ValueError("Profile name already exists in this account") from None

        return ProfileResponse(
            profile_id=profile.profile_id,
            account_id=profile.account_id,
            name=profile.name,
            avatar_url=profile.avatar_url,
            is_kids=profile.is_kids,
            created_at=profile.created_at,
        )

    async def list_profiles(self, account_id: uuid.UUID) -> list[ProfileResponse] | None:
        """List all profiles for an account."""
        account = await self._session.get(Account, account_id)
        if account is None:
            return None

        result = await self._session.execute(
            select(Profile).where(Profile.account_id == account_id).order_by(Profile.created_at)
        )
        profiles = result.scalars().all()
        return [
            ProfileResponse(
                profile_id=p.profile_id,
                account_id=p.account_id,
                name=p.name,
                avatar_url=p.avatar_url,
                is_kids=p.is_kids,
                created_at=p.created_at,
            )
            for p in profiles
        ]

    async def get_profile(self, profile_id: uuid.UUID) -> ProfileResponse | None:
        """Get a single profile by id."""
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            return None
        return ProfileResponse(
            profile_id=profile.profile_id,
            account_id=profile.account_id,
            name=profile.name,
            avatar_url=profile.avatar_url,
            is_kids=profile.is_kids,
            created_at=profile.created_at,
        )

    async def update_profile(
        self, profile_id: uuid.UUID, data: ProfileUpdate
    ) -> ProfileResponse | None:
        """Partially update a profile. Raises ValueError on conflict."""
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            return None

        if data.name is not None:
            profile.name = data.name
        if data.avatar_url is not None:
            profile.avatar_url = data.avatar_url
        if data.is_kids is not None:
            profile.is_kids = data.is_kids

        try:
            await self._session.flush()
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise ValueError("Profile name already exists in this account") from None

        return ProfileResponse(
            profile_id=profile.profile_id,
            account_id=profile.account_id,
            name=profile.name,
            avatar_url=profile.avatar_url,
            is_kids=profile.is_kids,
            created_at=profile.created_at,
        )

    async def delete_profile(self, profile_id: uuid.UUID) -> bool:
        """Delete a profile and cascade playback data. Returns True if deleted."""
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            return False

        # Manual cascade for playback data
        await self._session.execute(
            text("DELETE FROM playback_progress WHERE profile_id = :pid"),
            {"pid": profile_id},
        )
        await self._session.execute(
            text("DELETE FROM watch_history WHERE profile_id = :pid"),
            {"pid": profile_id},
        )
        await self._session.delete(profile)
        await self._session.flush()
        await self._session.commit()
        return True
