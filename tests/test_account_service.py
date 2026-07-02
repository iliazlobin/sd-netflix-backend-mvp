"""White-box tests — AccountService."""

from __future__ import annotations

import uuid

import pytest

from netflix.schemas import AccountCreate
from netflix.services import AccountService


@pytest.mark.asyncio
async def test_create_account(session):
    """Creating an account returns the expected fields."""
    service = AccountService(session)
    result = await service.create_account(AccountCreate(email="test@example.com"))
    assert result.email == "test@example.com"
    assert result.account_id is not None
    assert result.created_at is not None


@pytest.mark.asyncio
async def test_create_duplicate_email_raises(session):
    """Creating an account with an existing email raises ValueError."""
    service = AccountService(session)
    await service.create_account(AccountCreate(email="dup@example.com"))
    with pytest.raises(ValueError, match="Email already registered"):
        await service.create_account(AccountCreate(email="dup@example.com"))


@pytest.mark.asyncio
async def test_get_account_found(session):
    """Getting an existing account returns the correct data."""
    service = AccountService(session)
    created = await service.create_account(AccountCreate(email="getme@example.com"))
    fetched = await service.get_account(created.account_id)
    assert fetched is not None
    assert fetched.email == "getme@example.com"
    assert fetched.account_id == created.account_id


@pytest.mark.asyncio
async def test_get_account_not_found(session):
    """Getting a non-existent account returns None."""
    service = AccountService(session)
    result = await service.get_account(uuid.uuid4())
    assert result is None
