from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FASTMILE_", extra="ignore")

    router_host: str = "192.168.0.1"
    router_timeout_seconds: int = 30
    cache_ttl_seconds: int = 15
    cache_stale_seconds: int = 5
