import asyncio

from app.core.cache import TTLCache


def test_caches_within_ttl() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=60)
    calls = 0

    async def factory() -> int:
        nonlocal calls
        calls += 1
        return 42

    async def main() -> None:
        assert await cache.get_or_set("k", factory) == 42
        assert await cache.get_or_set("k", factory) == 42  # served from cache
        assert calls == 1

    asyncio.run(main())


def test_recomputes_after_expiry() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=0)  # everything is immediately stale
    calls = 0

    async def factory() -> int:
        nonlocal calls
        calls += 1
        return calls

    async def main() -> None:
        assert await cache.get_or_set("k", factory) == 1
        assert await cache.get_or_set("k", factory) == 2  # recomputed
        assert calls == 2

    asyncio.run(main())


def test_separate_keys_and_clear() -> None:
    cache: TTLCache[str] = TTLCache(ttl_seconds=60)

    async def main() -> None:
        assert await cache.get_or_set("a", lambda: _const("A")) == "A"
        assert await cache.get_or_set("b", lambda: _const("B")) == "B"
        cache.clear()
        assert await cache.get_or_set("a", lambda: _const("A2")) == "A2"  # recomputed

    async def _const(v: str) -> str:
        return v

    asyncio.run(main())
