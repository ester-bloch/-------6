from __future__ import annotations

import datetime as _dt
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .core.logging import configure_logging, get_logger
from .core.settings import settings
from .core.cache import TTLCache
from .core.exceptions import AppError, ValidationError
from .providers.base import default_context
from .providers.overpass import OverpassProvider
from .providers.openweather import OpenWeatherProvider
from .providers.nps import NPSAlertsProvider
from .services.location_service import LocationService
from .services.conditions_service import ConditionsService
from .services.risk_service import RiskService
from .models.common import ToolResponse, ToolErrorResponse, Provenance
from .models.common import Coordinates
from .utils.ids import coords_from_location_id
from .tools.schemas import (
    SearchLocationsInput,
    GetLocationProfileInput,
    GetRealTimeConditionsInput,
    RiskAndSafetySummaryInput,
)

logger = get_logger(__name__)


def _now_iso() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class OutdoorIntelligenceServer:
    def __init__(self):
        configure_logging()
        self.mcp = FastMCP(settings.server_name)

        # infra
        self._cache = TTLCache(default_ttl_s=settings.cache_ttl_s)

        # providers
        ctx = default_context()
        self._ctx = ctx
        self._overpass = OverpassProvider(ctx)
        self._weather = OpenWeatherProvider(ctx)
        self._nps = NPSAlertsProvider(ctx)

        # services
        self._locations = LocationService(self._overpass)
        self._conditions = ConditionsService(self._weather, self._nps)
        self._risk = RiskService()

        self._register_tools()

    async def close(self) -> None:
        await self._ctx.http.close()

    def _ok(self, data: dict, *, provenance: Provenance, cache_meta: dict | None = None, warnings: list[str] | None = None):
        resp = ToolResponse(ok=True, data=data, provenance=provenance, cache=cache_meta, warnings=warnings or [])
        return resp.model_dump()

    def _err(self, err: AppError, *, provenance: Provenance | None = None, warnings: list[str] | None = None):
        prov = provenance or Provenance(sources=[])
        resp = ToolErrorResponse(ok=False, error=err.to_dict(), provenance=prov, warnings=warnings or [])
        return resp.model_dump()

    def _coords_from_input(self, location_id: str | None, lat: float | None, lon: float | None) -> Coordinates:
        if location_id:
            return coords_from_location_id(location_id)
        if lat is None or lon is None:
            raise ValidationError(code="missing_coordinates", message="Provide either location_id or lat/lon.")
        return Coordinates(lat=lat, lon=lon)

    def _register_tools(self) -> None:
        @self.mcp.tool()
        async def search_locations(args: SearchLocationsInput) -> dict[str, Any]:
            """Search locations (POIs, trails, parks) near coordinates using OpenStreetMap Overpass."""
            key = f"search:{args.lat:.5f}:{args.lon:.5f}:{args.radius_km:.2f}:{args.query.lower()}:{args.limit}"
            try:
                async def factory():
                    return await self._locations.search(args.lat, args.lon, args.radius_km, args.query, limit=args.limit)

                (locations, prov), cache_meta = await self._cache.get_or_set(key, factory, ttl_s=min(settings.cache_ttl_s, 900))
                data = {"locations": [l.model_dump() for l in locations]}
                prov.fetched_at_iso = _now_iso()
                return self._ok(data, provenance=prov, cache_meta=cache_meta)
            except AppError as e:
                return self._err(e, provenance=Provenance(sources=["osm_overpass"]))
            except Exception as e:
                return self._err(AppError(code="internal_error", message="Unhandled error.", details={"where": "search_locations"}, cause=e), provenance=Provenance(sources=["osm_overpass"]))

        @self.mcp.tool()
        async def get_location_profile(args: GetLocationProfileInput) -> dict[str, Any]:
            """Get a normalized profile for a location, including nearby features."""
            try:
                coords = self._coords_from_input(args.location_id, args.lat, args.lon)

                # If we got a location_id, do a lightweight re-hydration by searching its name isn't possible.
                # Instead, we create a synthetic Location anchor from coordinates.
                from .models.location import Location
                location = Location(
                    id=args.location_id or f"coord:{coords.lat:.6f}:{coords.lon:.6f}",
                    name="Location Anchor",
                    kind="region",
                    center=coords,
                    source="fusion",
                    confidence=0.6,
                )

                key = f"profile:{coords.lat:.5f}:{coords.lon:.5f}:{args.features_radius_km:.2f}"
                async def factory():
                    return await self._locations.profile(location, features_radius_km=args.features_radius_km)

                (profile, prov), cache_meta = await self._cache.get_or_set(key, factory, ttl_s=min(settings.cache_ttl_s, 900))
                prov.fetched_at_iso = _now_iso()
                data = {"profile": profile.model_dump()}
                warnings = []
                if args.location_id and location.name == "Location Anchor":
                    warnings.append("location_id resolution uses embedded coordinates; name is a synthetic anchor.")
                return self._ok(data, provenance=prov, cache_meta=cache_meta, warnings=warnings)
            except AppError as e:
                return self._err(e, provenance=Provenance(sources=["osm_overpass"]))
            except Exception as e:
                return self._err(AppError(code="internal_error", message="Unhandled error.", details={"where": "get_location_profile"}, cause=e), provenance=Provenance(sources=["osm_overpass"]))

        @self.mcp.tool()
        async def get_real_time_conditions(args: GetRealTimeConditionsInput) -> dict[str, Any]:
            """Get real-time weather and alerts for a location."""
            try:
                coords = self._coords_from_input(args.location_id, args.lat, args.lon)
                key = f"conditions:{coords.lat:.5f}:{coords.lon:.5f}"
                async def factory():
                    return await self._conditions.real_time(coords.lat, coords.lon)

                (conditions, prov), cache_meta = await self._cache.get_or_set(key, factory, ttl_s=min(settings.cache_ttl_s, 300))
                data = {"conditions": conditions.model_dump()}
                return self._ok(data, provenance=prov, cache_meta=cache_meta)
            except AppError as e:
                return self._err(e, provenance=Provenance(sources=["openweather", "nps_alerts"]))
            except Exception as e:
                return self._err(AppError(code="internal_error", message="Unhandled error.", details={"where": "get_real_time_conditions"}, cause=e), provenance=Provenance(sources=["openweather", "nps_alerts"]))

        @self.mcp.tool()
        async def risk_and_safety_summary(args: RiskAndSafetySummaryInput) -> dict[str, Any]:
            """Compute a deterministic risk score (0-100) with evidence and recommendations."""
            try:
                coords = self._coords_from_input(args.location_id, args.lat, args.lon)

                # gather profile (feature_count) + conditions
                profile_key = f"profile_count:{coords.lat:.5f}:{coords.lon:.5f}:{args.features_radius_km:.2f}"
                async def profile_factory():
                    from .models.location import Location
                    anchor = Location(id=args.location_id or "anchor", name="Location Anchor", kind="region", center=coords, source="fusion", confidence=0.6)
                    profile, prov = await self._locations.profile(anchor, features_radius_km=args.features_radius_km)
                    return (len(profile.features), prov)

                (feature_count, prov1), _ = await self._cache.get_or_set(profile_key, profile_factory, ttl_s=min(settings.cache_ttl_s, 900))

                cond_key = f"conditions:{coords.lat:.5f}:{coords.lon:.5f}"
                async def cond_factory():
                    return await self._conditions.real_time(coords.lat, coords.lon)

                (conditions, prov2), cache_meta = await self._cache.get_or_set(cond_key, cond_factory, ttl_s=min(settings.cache_ttl_s, 300))

                assessment = self._risk.assess(conditions=conditions, feature_count=feature_count, when_iso=args.when_iso)

                prov = Provenance(
                    sources=list({*(prov1.sources or []), *(prov2.sources or [])}),
                    fetched_at_iso=_now_iso(),
                    notes=[],
                )
                data = {"risk": assessment.model_dump()}
                return self._ok(data, provenance=prov, cache_meta=cache_meta)
            except AppError as e:
                return self._err(e, provenance=Provenance(sources=["osm_overpass", "openweather", "nps_alerts"]))
            except Exception as e:
                return self._err(AppError(code="internal_error", message="Unhandled error.", details={"where": "risk_and_safety_summary"}, cause=e), provenance=Provenance(sources=["osm_overpass", "openweather", "nps_alerts"]))

    async def run(self) -> None:
        logger.info("starting", server=settings.server_name)
        await self.mcp.run(transport="stdio")
