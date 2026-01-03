from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field

from .common import Coordinates


class Location(BaseModel):
    id: str
    name: str
    kind: Literal["poi", "trail", "park", "region", "unknown"] = "unknown"
    center: Coordinates
    bbox: Optional[dict[str, float]] = None
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    source: str = "osm"


class NearbyFeature(BaseModel):
    kind: str
    name: str | None = None
    center: Coordinates | None = None
    tags: dict[str, str] = Field(default_factory=dict)


class LocationProfile(BaseModel):
    location: Location
    features: list[NearbyFeature] = Field(default_factory=list)
    summary: dict[str, str] = Field(default_factory=dict)
