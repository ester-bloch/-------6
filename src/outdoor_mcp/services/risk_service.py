from __future__ import annotations

import datetime as _dt
import math
from ..models.risk import RiskAssessment, RiskBreakdown
from ..models.conditions import RealTimeConditions
from ..models.common import Provenance


class RiskService:
    def __init__(self):
        pass

    def _weather_risk(self, conditions: RealTimeConditions) -> int:
        w = conditions.weather
        score = 0.0
        if w.temperature_c is not None:
            if w.temperature_c <= 0:
                score += 35
            elif w.temperature_c >= 35:
                score += 35
            elif w.temperature_c >= 30:
                score += 20
        if w.wind_m_s is not None:
            if w.wind_m_s >= 15:
                score += 35
            elif w.wind_m_s >= 10:
                score += 20
            elif w.wind_m_s >= 7:
                score += 10
        if w.precipitation_mm_1h is not None:
            if w.precipitation_mm_1h >= 10:
                score += 25
            elif w.precipitation_mm_1h >= 2:
                score += 10
        return int(min(100, round(score)))

    def _alerts_risk(self, conditions: RealTimeConditions) -> int:
        if not conditions.alerts:
            return 0
        # Basic heuristic: more alerts => higher risk
        return min(100, 20 + 15 * len(conditions.alerts))

    def _remoteness_risk(self, feature_count: int) -> int:
        # Fewer amenities/features nearby may imply higher remoteness risk.
        if feature_count <= 5:
            return 70
        if feature_count <= 15:
            return 45
        if feature_count <= 30:
            return 25
        return 10

    def _daylight_risk(self, when_iso: str | None) -> int:
        # Without timezone + sunrise API, keep conservative deterministic heuristic.
        if not when_iso:
            return 10
        try:
            dt = _dt.datetime.fromisoformat(when_iso.replace("Z", "+00:00"))
            hour = dt.hour
        except Exception:
            return 15
        if 0 <= hour <= 5:
            return 55
        if 6 <= hour <= 7 or 18 <= hour <= 20:
            return 25
        return 10

    def assess(self, conditions: RealTimeConditions, feature_count: int, when_iso: str | None = None) -> RiskAssessment:
        weather = self._weather_risk(conditions)
        alerts = self._alerts_risk(conditions)
        remoteness = self._remoteness_risk(feature_count)
        daylight = self._daylight_risk(when_iso)

        # Weighted score (deterministic)
        score = int(min(100, round(0.45 * weather + 0.25 * alerts + 0.20 * remoteness + 0.10 * daylight)))

        recs: list[str] = []
        uncertainties: list[str] = []

        if weather >= 40:
            recs.append("Consider rescheduling or reducing exposure time due to weather risk.")
        if remoteness >= 50:
            recs.append("Carry extra water/food and ensure offline navigation; nearby amenities may be limited.")
        if daylight >= 40:
            recs.append("Avoid night travel; plan routes with sufficient daylight buffer.")
        if alerts >= 35:
            recs.append("Review active alerts and follow local authority guidance.")

        if conditions.weather.description and "Demo weather" in conditions.weather.description:
            uncertainties.append("Weather is in demo mode (no OPENWEATHER_API_KEY). Risk score may be underestimated/overestimated.")
        if not conditions.alerts:
            uncertainties.append("Alert coverage may be partial (NPS geo alerts not supported directly).")

        evidence = {
            "weather": conditions.weather.model_dump(),
            "alerts_count": len(conditions.alerts),
            "feature_count": feature_count,
            "when_iso": when_iso,
        }

        return RiskAssessment(
            risk_score=score,
            breakdown=RiskBreakdown(weather=weather, alerts=alerts, remoteness=remoteness, daylight=daylight),
            evidence=evidence,
            recommendations=recs,
            uncertainties=uncertainties,
        )
