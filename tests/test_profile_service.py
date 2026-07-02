"""White-box tests — ProfileService."""

from __future__ import annotations

import uuid

import pytest

from netflix.schemas import AccountCreate, ProfileCreate, ProfileUpdate
from netflix.services import AccountService, ProfileService


@pytest.fixture
async def account(session):
    """Create an account fixture."""
    svc = AccountService(session)
    return await svc.create_account(AccountCreate(email="profile-test@example.com"))


@pytest.mark.asyncio
async def test_create_profile(session, account):
    """Creating a profile returns expected fields."""
    svc = ProfileService(session)
    result = await svc.create_profile(
        ProfileCreate(account_id=account.account_id, name="Test Profile")
    )
    assert result.name == "Test Profile"
    assert result.is_kids is False


@pytest.mark.asyncio
async def test_create_profile_unknown_account(session):
    """Creating a profile with an unknown account raises ValueError."""
    svc = ProfileService(session)
    with pytest.raises(ValueError, match="Account not found"):
        await svc.create_profile(ProfileCreate(account_id=uuid.uuid4(), name="Ghost"))


@pytest.mark.asyncio
async def test_create_duplicate_profile_name(session, account):
    """Creating a profile with a duplicate name within the same account raises."""
    svc = ProfileService(session)
    await svc.create_profile(ProfileCreate(account_id=account.account_id, name="Unique"))
    with pytest.raises(ValueError, match="already exists"):
        await svc.create_profile(ProfileCreate(account_id=account.account_id, name="Unique"))


@pytest.mark.asyncio
async def test_list_profiles(session, account):
    """Listing profiles returns all profiles for an account."""
    svc = ProfileService(session)
    await svc.create_profile(ProfileCreate(account_id=account.account_id, name="P1"))
    await svc.create_profile(ProfileCreate(account_id=account.account_id, name="P2"))
    profiles = await svc.list_profiles(account.account_id)
    assert profiles is not None
    assert len(profiles) == 2


@pytest.mark.asyncio
async def test_update_profile_name(session, account):
    """Updating a profile's name works."""
    svc = ProfileService(session)
    created = await svc.create_profile(ProfileCreate(account_id=account.account_id, name="Before"))
    updated = await svc.update_profile(created.profile_id, ProfileUpdate(name="After"))
    assert updated is not None
    assert updated.name == "After"


@pytest.mark.asyncio
async def test_delete_profile(session, account):
    """Deleting a profile returns True and it can't be found."""
    svc = ProfileService(session)
    created = await svc.create_profile(
        ProfileCreate(account_id=account.account_id, name="DeleteMe")
    )
    deleted = await svc.delete_profile(created.profile_id)
    assert deleted is True
    fetched = await svc.get_profile(created.profile_id)
    assert fetched is None


@pytest.mark.asyncio
async def test_delete_unknown_profile(session):
    """Deleting a non-existent profile returns False."""
    svc = ProfileService(session)
    result = await svc.delete_profile(uuid.uuid4())
    assert result is False
