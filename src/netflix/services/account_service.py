"""AccountService — create and lookup accounts."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.models import Account
from netflix.schemas import AccountCreate, AccountResponse


class AccountService:
    """Business logic for account operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_account(self, data: AccountCreate) -> AccountResponse:
        """Create a new account. Raises ValueError on duplicate email."""
        existing = await self._session.execute(select(Account).where(Account.email == data.email))
        if existing.scalar_one_or_none() is not None:
            raise ValueError("Email already registered")

        account = Account(email=data.email)
        self._session.add(account)
        await self._session.flush()
        return AccountResponse(
            account_id=account.account_id,
            email=account.email,
            created_at=account.created_at,
        )

    async def get_account(self, account_id: uuid.UUID) -> AccountResponse | None:
        """Look up an account by id."""
        result = await self._session.execute(
            select(Account).where(Account.account_id == account_id)
        )
        account = result.scalar_one_or_none()
        if account is None:
            return None
        return AccountResponse(
            account_id=account.account_id,
            email=account.email,
            created_at=account.created_at,
        )
