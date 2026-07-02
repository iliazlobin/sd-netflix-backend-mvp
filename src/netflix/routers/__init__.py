"""Routers — re-export for convenient imports."""

from netflix.routers.accounts import router as accounts_router
from netflix.routers.health import router as health_router
from netflix.routers.home import router as home_router
from netflix.routers.playback import router as playback_router
from netflix.routers.profiles import router as profiles_router
from netflix.routers.search import router as search_router
from netflix.routers.streaming import router as streaming_router
from netflix.routers.titles import router as titles_router

__all__ = [
    "health_router",
    "accounts_router",
    "home_router",
    "titles_router",
    "streaming_router",
    "playback_router",
    "profiles_router",
    "search_router",
]
