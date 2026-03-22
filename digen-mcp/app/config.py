"""Application configuration for digen-mcp."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file='.env', env_prefix='DIGEN_', extra='ignore')

    provider: str = Field(default='mock')
    api_base_url: str | None = Field(default=None)
    api_token: str | None = Field(default=None)
    playwright_base_url: str | None = Field(default=None)
    playwright_username: str | None = Field(default=None)
    playwright_password: str | None = Field(default=None)
    db_path: str = Field(default='./data/digen.db')
    temp_dir: str = Field(default='./tmp')
    redis_url: str | None = Field(default=None)
    request_timeout_seconds: float = Field(default=30.0)
    retry_attempts: int = Field(default=3)
    log_level: str = Field(default='INFO')
    result_url_ttl_seconds: int = Field(default=3600)
    http_host: str = Field(default='127.0.0.1')
    http_port: int = Field(default=8000)

    @property
    def db_file(self) -> Path:
        return Path(self.db_path).expanduser().resolve()

    @property
    def temp_path(self) -> Path:
        return Path(self.temp_dir).expanduser().resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
