"""Schemas — re-export for convenient imports."""

from netflix.schemas.account import AccountCreate, AccountCreateRequest, AccountResponse
from netflix.schemas.home import (
    ContinueWatchingItem,
    GenreRow,
    GenreRowItem,
    HomePageResponse,
    TrendingItem,
)
from netflix.schemas.playback import HeartbeatRequest, HeartbeatResponse
from netflix.schemas.profile import (
    ProfileCreate,
    ProfileCreateRequest,
    ProfileResponse,
    ProfileUpdate,
)
from netflix.schemas.search import SearchResponse, SearchResult
from netflix.schemas.title import CastMemberOut, GenreOut, TitleDetailResponse, TitleListItem

__all__ = [
    "AccountCreate",
    "AccountCreateRequest",
    "AccountResponse",
    "ContinueWatchingItem",
    "GenreRow",
    "GenreRowItem",
    "HomePageResponse",
    "TrendingItem",
    "CastMemberOut",
    "GenreOut",
    "TitleDetailResponse",
    "TitleListItem",
    "ProfileCreate",
    "ProfileCreateRequest",
    "ProfileResponse",
    "ProfileUpdate",
    "HeartbeatRequest",
    "HeartbeatResponse",
    "SearchResult",
    "SearchResponse",
]
