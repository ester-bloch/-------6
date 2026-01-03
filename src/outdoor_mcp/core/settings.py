from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    server_name: str = Field(default="Outdoor Intelligence")
    overpass_url: str = Field(default="https://overpass-api.de/api/interpreter")
    openweather_api_key: str = Field(default="")
    openweather_base_url: str = Field(default="https://api.openweathermap.org/data/2.5")
    nps_api_key: str = Field(default="")
    nps_api_base_url: str = Field(default="https://developer.nps.gov/api/v1")

    http_timeout_s: float = Field(default=12)
    http_max_retries: int = Field(default=2)

    cache_ttl_s: int = Field(default=600)
    rate_limit_rps: float = Field(default=3)

    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=False)

    # Demo mode: if no API keys available, tools still return deterministic synthetic outputs.
    demo_fallback: bool = Field(default=True)


settings = Settings()
