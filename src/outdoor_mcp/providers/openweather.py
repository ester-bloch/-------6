from __future__ import annotations

import datetime as _dt
from typing import Any, Optional

from ..core.exceptions import ProviderError
from ..core.settings import settings
from ..models.conditions import WeatherConditions
from ..models.common import Coordinates
from .base import ProviderContext


class OpenWeatherProvider:
    name = "openweather"

    def __init__(self, ctx: ProviderContext):
        self._ctx = ctx

    async def get_weather(self, lat: float, lon: float) -> WeatherConditions:
        # Demo fallback if no API key
        if not settings.openweather_api_key and settings.demo_fallback:
            now = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
            return WeatherConditions(
                at=Coordinates(lat=lat, lon=lon),
                observed_at_iso=now,
                temperature_c=18.0,
                feels_like_c=17.0,
                wind_m_s=3.5,
                precipitation_mm_1h=0.0,
                humidity_pct=55,
                description="Demo weather (no OPENWEATHER_API_KEY configured).",
                is_demo=True,
            )
        if not settings.openweather_api_key:
            raise ProviderError(code="missing_api_key", message="OPENWEATHER_API_KEY is required for real weather data.")

        await self._ctx.limiter.acquire()
        url = f"{settings.openweather_base_url}/weather"
        resp = await self._ctx.http.request(
            "GET",
            url,
            params={"lat": lat, "lon": lon, "appid": settings.openweather_api_key, "units": "metric"},
            timeout=settings.openweather_timeout_s,
        )
        if resp.status_code != 200:
            raise ProviderError(code="openweather_http_error", message="OpenWeather returned error", details={"status": resp.status_code, "text": resp.text[:500]})

        data = resp.json()
        now = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        return WeatherConditions(
            at=Coordinates(lat=lat, lon=lon),
            observed_at_iso=now,
            temperature_c=(data.get("main") or {}).get("temp"),
            feels_like_c=(data.get("main") or {}).get("feels_like"),
            wind_m_s=(data.get("wind") or {}).get("speed"),
            precipitation_mm_1h=(data.get("rain") or {}).get("1h") or 0.0,
            humidity_pct=(data.get("main") or {}).get("humidity"),
            description=((data.get("weather") or [{}])[0] or {}).get("description"),
            is_demo=False,
        )
