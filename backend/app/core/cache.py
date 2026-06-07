"""Tiny in-process TTL cache for the read-only API.

All data changes once a day via ETL, so caching DB results for a few minutes
removes a per-request round-trip to Supabase (and the occasional cold-connection
latency spike) without serving meaningfully stale responses. Values are cached
(not ORM objects), so they outlive the request's session safely.
"""

import time
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Async cache-aside helper keyed by string, with a per-instance TTL."""

    def __init__(self, ttl_seconds: float) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, T]] = {}

    async def get_or_set(self, key: str, factory: Callable[[], Awaitable[T]]) -> T:
        """Return the cached value for ``key`` or compute, store, and return it.

        ``factory`` runs only on a miss; if it raises, nothing is cached.
        """
        now = time.monotonic()
        cached = self._store.get(key)
        if cached is not None and now - cached[0] < self._ttl:
            return cached[1]
        value = await factory()
        self._store[key] = (now, value)
        return value

    def clear(self) -> None:
        self._store.clear()
