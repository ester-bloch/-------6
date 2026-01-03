from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from .conditions import RealTimeConditions


class RiskBreakdown(BaseModel):
    weather: int = Field(..., ge=0, le=100)
    alerts: int = Field(..., ge=0, le=100)
    remoteness: int = Field(..., ge=0, le=100)
    daylight: int = Field(..., ge=0, le=100)


class RiskAssessment(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    breakdown: RiskBreakdown
    evidence: dict = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
