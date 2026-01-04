from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry:
    value: Any
    expires_at: float
    created_at: float


class TTLCache:
    def __init__(self, default_ttl_s: int):
        self._default_ttl_s = default_ttl_s
        self._store: dict[str, CacheEntry] = {}
        self._inflight: dict[str, asyncio.Task] = {}
        self._inflight_lock = asyncio.Lock()

    def get(self, key: str) -> Optional[CacheEntry]:
        entry = self._store.get(key)
        if not entry:
            return None
        if time.time() >= entry.expires_at:
            self._store.pop(key, None)
            return None
        return entry

    def set(self, key: str, value: Any, ttl_s: Optional[int] = None) -> None:
        ttl = ttl_s if ttl_s is not None else self._default_ttl_s
        now = time.time()
        self._store[key] = CacheEntry(value=value, expires_at=now + ttl, created_at=now)

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], "Any"],
        ttl_s: Optional[int] = None,
    ):
        entry = self.get(key)
        if entry:
            return entry.value, {"hit": True, "age_s": int(time.time() - entry.created_at), "ttl_s": int(entry.expires_at - entry.created_at)}
        created = False
        async with self._inflight_lock:
            task = self._inflight.get(key)
            if task is None:
                task = asyncio.create_task(factory())
                self._inflight[key] = task
                created = True
        try:
            value = await task
        except Exception:
            if created:
                async with self._inflight_lock:
                    if self._inflight.get(key) is task:
                        self._inflight.pop(key, None)
            raise

        if created:
            self.set(key, value, ttl_s=ttl_s)
            async with self._inflight_lock:
                if self._inflight.get(key) is task:
                    self._inflight.pop(key, None)
            return value, {"hit": False, "age_s": 0, "ttl_s": ttl_s if ttl_s is not None else self._default_ttl_s}

        entry = self.get(key)
        if entry:
            return entry.value, {"hit": True, "age_s": int(time.time() - entry.created_at), "ttl_s": int(entry.expires_at - entry.created_at)}
        return value, {"hit": False, "age_s": 0, "ttl_s": ttl_s if ttl_s is not None else self._default_ttl_s}
