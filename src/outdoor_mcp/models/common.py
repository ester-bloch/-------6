from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class Provenance(BaseModel):
    sources: list[str] = Field(default_factory=list)
    fetched_at_iso: Optional[str] = None
    notes: list[str] = Field(default_factory=list)


class CacheMeta(BaseModel):
    hit: bool
    age_s: int
    ttl_s: int


class ToolResponse(BaseModel):
    ok: bool = True
    data: dict
    provenance: Provenance = Field(default_factory=Provenance)
    cache: Optional[CacheMeta] = None
    warnings: list[str] = Field(default_factory=list)


class ToolErrorResponse(BaseModel):
    ok: bool = False
    error: dict
    provenance: Provenance = Field(default_factory=Provenance)
    warnings: list[str] = Field(default_factory=list)
