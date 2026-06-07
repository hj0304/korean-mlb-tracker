"""Dashboard unit test for the empty branch; the populated feed is covered by
the integration test (real Postgres) since it needs a join + max() query."""

import asyncio
from typing import Any

from app.api.v1.dashboard import _build_today


class _NoGamesSession:
    """execute().scalar() returns None — i.e. game_logs is empty."""

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        class _Result:
            def scalar(self) -> None:
                return None

        return _Result()


def test_build_today_empty() -> None:
    out = asyncio.run(_build_today(_NoGamesSession()))  # type: ignore[arg-type]
    assert out.date is None
    assert out.games == []
