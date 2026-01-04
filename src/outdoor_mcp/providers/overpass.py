from __future__ import annotations

import datetime as _dt
import re
from typing import Any

from ..core.exceptions import ProviderError
from ..core.logging import get_logger
from ..models.location import Location, NearbyFeature
from ..models.common import Coordinates
from ..core.settings import settings
from .base import ProviderContext

logger = get_logger(__name__)


class OverpassProvider:
    name = "osm_overpass"

    def __init__(self, ctx: ProviderContext):
        self._ctx = ctx

    async def search_locations(self, lat: float, lon: float, radius_km: float, query: str | None, limit: int = 10) -> list[Location]:
        await self._ctx.limiter.acquire()
        radius_m = int(max(100, radius_km * 1000))

        # Simple, robust query: search for named nodes/ways/relations matching query within radius.
        name_filter = ""
        if query:
            safe = re.escape(query)
            name_filter = f'[name~"{safe}",i]'
        q = f"""
        [out:json][timeout:25];
        (
          node(around:{radius_m},{lat},{lon}){name_filter};
          way(around:{radius_m},{lat},{lon}){name_filter};
          relation(around:{radius_m},{lat},{lon}){name_filter};
        );
        out center {limit};
        """

        resp = await self._ctx.http.request("POST", settings.overpass_url, data={"data": q}, timeout=settings.overpass_timeout_s)
        if resp.status_code != 200:
            raise ProviderError(code="overpass_http_error", message="Overpass API returned error", details={"status": resp.status_code, "text": resp.text[:500]})

        data = resp.json()
        elements = data.get("elements", [])
        results: list[Location] = []
        for el in elements[:limit]:
            name = (el.get("tags") or {}).get("name") or "Unknown"
            kind = "poi"
            if (el.get("tags") or {}).get("highway") == "path" or (el.get("tags") or {}).get("route") == "hiking":
                kind = "trail"
            if (el.get("tags") or {}).get("leisure") == "park":
                kind = "park"

            center = None
            if "lat" in el and "lon" in el:
                center = Coordinates(lat=float(el["lat"]), lon=float(el["lon"]))
            elif "center" in el:
                center = Coordinates(lat=float(el["center"]["lat"]), lon=float(el["center"]["lon"]))
            else:
                continue

            loc_id = f"osm:{el.get('type','el')}:{el.get('id')}:{center.lat:.6f}:{center.lon:.6f}"
            results.append(Location(id=loc_id, name=name, kind=kind, center=center, source=self.name, confidence=0.75))
        return results

    async def nearby_features(self, lat: float, lon: float, radius_km: float) -> list[NearbyFeature]:
        await self._ctx.limiter.acquire()
        radius_m = int(max(100, radius_km * 1000))
        q = f"""
        [out:json][timeout:25];
        (
          node(around:{radius_m},{lat},{lon})[amenity];
          node(around:{radius_m},{lat},{lon})[tourism];
          node(around:{radius_m},{lat},{lon})[natural];
          way(around:{radius_m},{lat},{lon})[highway=path];
          relation(around:{radius_m},{lat},{lon})[route=hiking];
          node(around:{radius_m},{lat},{lon})[leisure=park];
        );
        out center 50;
        """
        resp = await self._ctx.http.request("POST", settings.overpass_url, data={"data": q}, timeout=settings.overpass_timeout_s)
        if resp.status_code != 200:
            raise ProviderError(code="overpass_http_error", message="Overpass API returned error", details={"status": resp.status_code, "text": resp.text[:500]})
        data = resp.json()
        features: list[NearbyFeature] = []
        for el in data.get("elements", [])[:50]:
            tags = el.get("tags") or {}
            name = tags.get("name")
            kind = tags.get("amenity") or tags.get("tourism") or tags.get("natural") or tags.get("leisure") or tags.get("highway") or tags.get("route") or "feature"
            center = None
            if "lat" in el and "lon" in el:
                center = Coordinates(lat=float(el["lat"]), lon=float(el["lon"]))
            elif "center" in el:
                center = Coordinates(lat=float(el["center"]["lat"]), lon=float(el["center"]["lon"]))
            features.append(NearbyFeature(kind=str(kind), name=name, center=center, tags={k: str(v) for k, v in tags.items() if isinstance(v,(str,int,float))}))
        return features
