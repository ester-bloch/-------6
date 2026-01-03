from __future__ import annotations

from typing import Protocol, Any
from ..core.http import HttpClient
from ..core.rate_limiter import RateLimiter
from ..core.settings import settings


class Provider(Protocol):
    name: str


class ProviderContext:
    def __init__(self, http: HttpClient, limiter: RateLimiter):
        self.http = http
        self.limiter = limiter


def default_context() -> ProviderContext:
    return ProviderContext(http=HttpClient(), limiter=RateLimiter(settings.rate_limit_rps))
