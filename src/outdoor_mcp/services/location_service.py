from __future__ import annotations

from typing import Optional
from ..providers.overpass import OverpassProvider
from ..models.location import LocationProfile
from ..models.common import Provenance


class LocationService:
    def __init__(self, overpass: OverpassProvider):
        self._overpass = overpass

    async def search(self, lat: float, lon: float, radius_km: float, query: Optional[str], limit: int = 10):
        locations = await self._overpass.search_locations(lat=lat, lon=lon, radius_km=radius_km, query=query, limit=limit)
        prov = Provenance(sources=[self._overpass.name])
        return locations, prov

    async def profile(self, location, features_radius_km: float = 3.0):
        features = await self._overpass.nearby_features(lat=location.center.lat, lon=location.center.lon, radius_km=features_radius_km)
        summary = {
            "feature_count": str(len(features)),
            "note": "Features are derived from OpenStreetMap tags via Overpass.",
        }
        prov = Provenance(sources=[self._overpass.name])
        return LocationProfile(location=location, features=features, summary=summary), prov
