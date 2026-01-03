from __future__ import annotations

import datetime as _dt
from typing import Any

from ..core.exceptions import ProviderError
from ..core.settings import settings
from ..models.conditions import Alert
from .base import ProviderContext


class NPSAlertsProvider:
    name = "nps_alerts"

    def __init__(self, ctx: ProviderContext):
        self._ctx = ctx

    async def get_alerts_near(self, lat: float, lon: float, radius_km: float = 50) -> list[Alert]:
        # NPS API does not support geo queries directly; we provide demo fallback unless API key + parkCode is used.
        if not settings.nps_api_key and settings.demo_fallback:
            return []
        if not settings.nps_api_key:
            raise ProviderError(code="missing_api_key", message="NPS_API_KEY is required for real NPS alerts.")
        # Minimal stub: keep provider in place for extensibility; return empty to avoid false claims.
        return []
