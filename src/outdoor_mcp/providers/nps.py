from __future__ import annotations

import datetime as _dt
from typing import Any
import math

from ..core.exceptions import ProviderError
from ..core.settings import settings
from ..models.conditions import Alert
from .base import ProviderContext


class NPSAlertsProvider:
    name = "nps_alerts"

    def __init__(self, ctx: ProviderContext):
        self._ctx = ctx

    def _distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    async def _nearest_park_code(self, lat: float, lon: float) -> str:
        best_code: str | None = None
        best_dist = float("inf")

        for page in range(settings.nps_parks_max_pages):
            params = {
                "api_key": settings.nps_api_key,
                "limit": settings.nps_parks_page_size,
                "start": page * settings.nps_parks_page_size,
            }
            url = f"{settings.nps_api_base_url}/parks"
            await self._ctx.limiter.acquire()
            resp = await self._ctx.http.request("GET", url, params=params, timeout=settings.nps_timeout_s)
            if resp.status_code != 200:
                raise ProviderError(
                    code="nps_http_error",
                    message="NPS parks endpoint returned error",
                    details={"status": resp.status_code, "text": resp.text[:500]},
                )
            data = resp.json()
            parks = data.get("data") or []
            if not parks:
                break

            for park in parks:
                try:
                    plat = float(park.get("latitude"))
                    plon = float(park.get("longitude"))
                except (TypeError, ValueError):
                    continue
                dist = self._distance_km(lat, lon, plat, plon)
                if dist < best_dist:
                    best_dist = dist
                    best_code = park.get("parkCode")

        if not best_code:
            raise ProviderError(code="nps_no_parks", message="Unable to resolve nearest park for alerts.")
        return best_code

    async def get_alerts_near(self, lat: float, lon: float, radius_km: float = 50) -> list[Alert]:
        # NPS API does not support geo queries directly; we do a best-effort nearest-park lookup.
        if not settings.nps_api_key and settings.demo_fallback:
            return []
        if not settings.nps_api_key:
            raise ProviderError(code="missing_api_key", message="NPS_API_KEY is required for real NPS alerts.")

        park_code = await self._nearest_park_code(lat, lon)
        params = {"api_key": settings.nps_api_key, "parkCode": park_code, "limit": settings.nps_alerts_limit}
        url = f"{settings.nps_api_base_url}/alerts"
        await self._ctx.limiter.acquire()
        resp = await self._ctx.http.request("GET", url, params=params, timeout=settings.nps_timeout_s)
        if resp.status_code != 200:
            raise ProviderError(
                code="nps_http_error",
                message="NPS alerts endpoint returned error",
                details={"status": resp.status_code, "text": resp.text[:500]},
            )

        payload = resp.json()
        alerts: list[Alert] = []
        for item in payload.get("data") or []:
            alerts.append(
                Alert(
                    source="nps",
                    title=item.get("title") or "Alert",
                    severity=(item.get("severity") or "unknown").lower(),
                    starts_at_iso=item.get("date"),
                    ends_at_iso=None,
                    url=item.get("url"),
                )
            )
        return alerts
