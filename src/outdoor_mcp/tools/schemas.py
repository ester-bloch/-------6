from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class SearchLocationsInput(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    radius_km: float = Field(default=5.0, ge=0.1, le=200, description="Search radius in kilometers")
    query: Optional[str] = Field(default=None, min_length=1, max_length=80, description="Name keyword (regex-like search)")
    limit: int = Field(default=10, ge=1, le=25)


class GetLocationProfileInput(BaseModel):
    location_id: Optional[str] = Field(default=None, description="Stable location identifier from search_locations")
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    features_radius_km: float = Field(default=3.0, ge=0.1, le=50)


class GetRealTimeConditionsInput(BaseModel):
    location_id: Optional[str] = None
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)


class RiskAndSafetySummaryInput(BaseModel):
    location_id: Optional[str] = None
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lon: Optional[float] = Field(default=None, ge=-180, le=180)
    when_iso: Optional[str] = Field(default=None, description="ISO datetime, e.g. 2026-01-03T18:00:00Z")
    features_radius_km: float = Field(default=3.0, ge=0.1, le=50)
