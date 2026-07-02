"""Application configuration via pydantic-settings.

All settings are driven by environment variables with sensible defaults
for local development. See .env.example for documentation.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed, env-driven configuration for the Netflix MVP backend."""

    # Database
    database_url: str = "postgresql+asyncpg://netflix:netflix@db:5432/netflix"

    # App
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # CORS
    cors_origins: str = "*"

    # Mock segments
    mock_segments_dir: str = "/app/data/segments"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
