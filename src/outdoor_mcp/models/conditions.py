from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from .common import Coordinates


class WeatherConditions(BaseModel):
    at: Coordinates
    observed_at_iso: str
    temperature_c: Optional[float] = None
    feels_like_c: Optional[float] = None
    wind_m_s: Optional[float] = None
    precipitation_mm_1h: Optional[float] = None
    humidity_pct: Optional[int] = Field(default=None, ge=0, le=100)
    description: Optional[str] = None


class Alert(BaseModel):
    source: str
    title: str
    severity: str = "unknown"
    starts_at_iso: Optional[str] = None
    ends_at_iso: Optional[str] = None
    url: Optional[str] = None


class RealTimeConditions(BaseModel):
    weather: WeatherConditions
    alerts: list[Alert] = Field(default_factory=list)
