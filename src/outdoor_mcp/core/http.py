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

    def _retry_delay(self, attempt: int) -> float:
        base = settings.http_retry_backoff_s * (2 ** attempt)
        return min(settings.http_retry_max_backoff_s, base)

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_body: Any = None,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(settings.http_max_retries + 1):
            try:
                resp = await self._client.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                )
                if resp.status_code in (429, 500, 502, 503, 504) and attempt < settings.http_max_retries:
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        await asyncio.sleep(min(float(retry_after), settings.http_retry_max_backoff_s))
                    else:
                        await asyncio.sleep(self._retry_delay(attempt))
                    continue
                return resp
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exc = e
                await asyncio.sleep(self._retry_delay(attempt))
        raise ProviderError(code="network_error", message="Network error while calling external provider.", details={"url": url}, cause=last_exc)
