"""Account routers — POST /api/v1/accounts, GET /api/v1/accounts/{account_id}."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.database import get_session
from netflix.schemas import AccountCreate, AccountCreateRequest, AccountResponse
from netflix.services import AccountService

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


@router.post("", status_code=201)
async def create_account(
    body: AccountCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> AccountResponse:
    """Create a new account."""
    service = AccountService(session)
    try:
        return await service.create_account(AccountCreate(email=body.email))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from None


@router.get("/{account_id}")
async def get_account(
    account_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> AccountResponse:
    """Look up an account by id."""
    service = AccountService(session)
    account = await service.get_account(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
