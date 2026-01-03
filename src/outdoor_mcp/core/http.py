from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx

from .settings import settings
from .exceptions import ProviderError
from .logging import get_logger

logger = get_logger(__name__)


class HttpClient:
    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout_s)

    async def close(self) -> None:
        await self._client.aclose()

    async def request(self, method: str, url: str, *, params: Optional[dict[str, Any]] = None, json_body: Any = None, headers: Optional[dict[str, str]] = None) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(settings.http_max_retries + 1):
            try:
                resp = await self._client.request(method, url, params=params, json=json_body, headers=headers)
                return resp
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exc = e
                await asyncio.sleep(0.2 * (2 ** attempt))
        raise ProviderError(code="network_error", message="Network error while calling external provider.", details={"url": url}, cause=last_exc)
