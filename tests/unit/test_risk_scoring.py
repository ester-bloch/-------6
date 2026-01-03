import datetime as dt
from outdoor_mcp.services.risk_service import RiskService
from outdoor_mcp.models.conditions import RealTimeConditions, WeatherConditions
from outdoor_mcp.models.common import Coordinates


def make_conditions(temp_c: float, wind: float, rain: float):
    return RealTimeConditions(
        weather=WeatherConditions(
            at=Coordinates(lat=0.0, lon=0.0),
            observed_at_iso=dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            temperature_c=temp_c,
            feels_like_c=temp_c,
            wind_m_s=wind,
            precipitation_mm_1h=rain,
            humidity_pct=50,
            description="test",
        ),
        alerts=[],
    )


def test_risk_increases_with_extreme_weather():
    svc = RiskService()
    low = svc.assess(make_conditions(20, 2, 0), feature_count=40).risk_score
    high = svc.assess(make_conditions(38, 16, 12), feature_count=40).risk_score
    assert high > low
