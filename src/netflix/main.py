"""FastAPI application factory for the Netflix MVP backend.

Exposes `create_app()` for uvicorn and tests.
Mounted routers: health, accounts, home, titles, streaming, playback, profiles, search.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from netflix.config import settings
from netflix.routers import (
    accounts_router,
    health_router,
    home_router,
    playback_router,
    profiles_router,
    search_router,
    streaming_router,
    titles_router,
)

logger = logging.getLogger("netflix")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan — startup/shutdown lifecycle."""
    logger.info("Starting Netflix MVP backend")
    yield
    logger.info("Shutting down Netflix MVP backend")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Netflix MVP",
        description="MVP streaming backend — catalog, search, playback, profiles",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    origins = [o.strip() for o in settings.cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routers
    app.include_router(health_router)
    app.include_router(accounts_router)
    app.include_router(home_router)
    app.include_router(titles_router)
    app.include_router(streaming_router)
    app.include_router(playback_router)
    app.include_router(profiles_router)
    app.include_router(search_router)

    return app


app = create_app()
