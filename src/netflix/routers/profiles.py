"""Profiles router — CRUD /api/v1/profiles."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from netflix.database import get_session
from netflix.schemas import (
    ProfileCreate,
    ProfileCreateRequest,
    ProfileResponse,
    ProfileUpdate,
)
from netflix.services import ProfileService

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


@router.get("")
async def list_profiles(
    account_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_session),
):
    """List all profiles for an account."""
    service = ProfileService(session)
    profiles = await service.list_profiles(account_id)
    if profiles is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"profiles": profiles}


@router.post("", status_code=201)
async def create_profile(
    body: ProfileCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> ProfileResponse:
    """Create a new profile."""
    service = ProfileService(session)
    try:
        return await service.create_profile(
            ProfileCreate(
                account_id=body.account_id,
                name=body.name,
                avatar_url=body.avatar_url,
                is_kids=body.is_kids,
            )
        )
    except ValueError as e:
        detail = str(e)
        if "Account" in detail:
            raise HTTPException(status_code=404, detail=detail) from None
        raise HTTPException(status_code=409, detail=detail) from None


@router.put("/{profile_id}")
async def update_profile(
    profile_id: uuid.UUID,
    body: ProfileUpdate,
    session: AsyncSession = Depends(get_session),
) -> ProfileResponse:
    """Partially update a profile."""
    service = ProfileService(session)
    try:
        profile = await service.update_profile(profile_id, body)
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from None


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    """Delete a profile and cascade playback data."""
    service = ProfileService(session)
    deleted = await service.delete_profile(profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
