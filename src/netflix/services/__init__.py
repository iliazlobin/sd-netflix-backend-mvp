"""Services — re-export for convenient imports."""

from netflix.services.account_service import AccountService
from netflix.services.catalog_service import CatalogService
from netflix.services.playback_service import PlaybackService
from netflix.services.profile_service import ProfileService
from netflix.services.search_service import SearchService
from netflix.services.streaming_service import StreamingService
from netflix.services.title_service import TitleService

__all__ = [
    "AccountService",
    "CatalogService",
    "TitleService",
    "StreamingService",
    "PlaybackService",
    "ProfileService",
    "SearchService",
]
