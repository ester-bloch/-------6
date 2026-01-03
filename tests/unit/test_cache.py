import asyncio
import pytest
from outdoor_mcp.core.cache import TTLCache


@pytest.mark.asyncio
async def test_cache_get_or_set_hits():
    cache = TTLCache(default_ttl_s=10)
    calls = {"n": 0}

    async def factory():
        calls["n"] += 1
        return {"x": 1}

    v1, meta1 = await cache.get_or_set("k", factory)
    v2, meta2 = await cache.get_or_set("k", factory)

    assert v1 == {"x": 1}
    assert v2 == {"x": 1}
    assert calls["n"] == 1
    assert meta1["hit"] is False
    assert meta2["hit"] is True
