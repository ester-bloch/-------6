from __future__ import annotations

import time
import asyncio
from dataclasses import dataclass

from .exceptions import RateLimitError


@dataclass
class TokenBucket:
    rate_per_s: float
    capacity: float
    tokens: float
    updated_at: float

    def refill(self) -> None:
        now = time.time()
        elapsed = now - self.updated_at
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate_per_s)
        self.updated_at = now

    def consume(self, amount: float = 1.0) -> bool:
        self.refill()
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False


class RateLimiter:
    def __init__(self, rate_per_s: float, capacity: float | None = None):
        cap = capacity if capacity is not None else max(1.0, rate_per_s)
        self._bucket = TokenBucket(rate_per_s=rate_per_s, capacity=cap, tokens=cap, updated_at=time.time())
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            if self._bucket.consume(1.0):
                return
        # simple backoff wait
        await asyncio.sleep(max(0.05, 1.0 / max(self._bucket.rate_per_s, 0.1)))
        async with self._lock:
            if not self._bucket.consume(1.0):
                raise RateLimitError(code="rate_limited", message="Rate limit exceeded. Please retry.")
