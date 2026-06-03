import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from app.services import mlb_client


def _call(
    fn: Callable[..., Awaitable[dict[str, Any]]], *args: Any, **kwargs: Any
) -> tuple[httpx.Request, dict[str, Any]]:
    """Run a client function against a mock transport, return (request, json)."""
    holder: dict[str, httpx.Request] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        holder["request"] = request
        return httpx.Response(200, json={"ok": True})

    async def main() -> dict[str, Any]:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(base_url=mlb_client.BASE_URL, transport=transport) as client:
            return await fn(client, *args, **kwargs)

    result = asyncio.run(main())
    return holder["request"], result


def test_get_person_path() -> None:
    req, data = _call(mlb_client.get_person, 808982)
    assert req.url.path == "/api/v1/people/808982"
    assert data == {"ok": True}


def test_get_season_stats_params() -> None:
    req, _ = _call(mlb_client.get_season_stats, 808982, 2026)
    assert req.url.path == "/api/v1/people/808982/stats"
    params = dict(req.url.params)
    assert params["stats"] == "season"
    assert params["group"] == "hitting,pitching"
    assert params["season"] == "2026"


def test_get_year_by_year_params() -> None:
    req, _ = _call(mlb_client.get_year_by_year, 673490)
    assert req.url.path == "/api/v1/people/673490/stats"
    params = dict(req.url.params)
    assert params["stats"] == "yearByYear"
    assert params["group"] == "hitting,pitching"


def test_get_schedule_params() -> None:
    req, _ = _call(mlb_client.get_schedule, "2026-05-18", team_id=119)
    assert req.url.path == "/api/v1/schedule"
    params = dict(req.url.params)
    assert params["sportId"] == "1"
    assert params["teamId"] == "119"
    assert params["date"] == "2026-05-18"


def test_get_boxscore_path() -> None:
    req, _ = _call(mlb_client.get_boxscore, 745700)
    assert req.url.path == "/api/v1/game/745700/boxscore"
