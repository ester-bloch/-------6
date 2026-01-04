from __future__ import annotations

import datetime as _dt
from ..providers.openweather import OpenWeatherProvider
from ..providers.nps import NPSAlertsProvider
from ..models.conditions import RealTimeConditions
from ..models.common import Provenance
from ..core.exceptions import ProviderError
from ..core.settings import settings


class ConditionsService:
    def __init__(self, weather: OpenWeatherProvider, nps_alerts: NPSAlertsProvider):
        self._weather = weather
        self._nps = nps_alerts

    async def real_time(self, lat: float, lon: float):
        warnings: list[str] = []
        weather = await self._weather.get_weather(lat=lat, lon=lon)
        if weather.is_demo:
            warnings.append("weather_demo_mode")

        alerts = []
        alerts_ok = False
        alerts_demo = False
        try:
            alerts = await self._nps.get_alerts_near(lat=lat, lon=lon)
            alerts_ok = True
        except ProviderError as e:
            warnings.append("alerts_unavailable")
        if not settings.nps_api_key and settings.demo_fallback:
            alerts_demo = True
            warnings.append("alerts_demo_mode")

        prov = Provenance(
            sources=[self._weather.name] + ([self._nps.name] if alerts_ok else []),
            fetched_at_iso=_dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        )
        return RealTimeConditions(weather=weather, alerts=alerts or []), prov, warnings, alerts_ok, alerts_demo
