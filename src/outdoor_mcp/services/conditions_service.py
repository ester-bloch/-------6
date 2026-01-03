from __future__ import annotations

import datetime as _dt
from ..providers.openweather import OpenWeatherProvider
from ..providers.nps import NPSAlertsProvider
from ..models.conditions import RealTimeConditions
from ..models.common import Provenance


class ConditionsService:
    def __init__(self, weather: OpenWeatherProvider, nps_alerts: NPSAlertsProvider):
        self._weather = weather
        self._nps = nps_alerts

    async def real_time(self, lat: float, lon: float):
        weather = await self._weather.get_weather(lat=lat, lon=lon)
        alerts = await self._nps.get_alerts_near(lat=lat, lon=lon)
        prov = Provenance(
            sources=[self._weather.name] + ([self._nps.name] if alerts is not None else []),
            fetched_at_iso=_dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        )
        return RealTimeConditions(weather=weather, alerts=alerts or []), prov
