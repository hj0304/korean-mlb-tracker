"""Thin async wrapper over the unofficial MLB Stats API.

This is the only module allowed to call ``statsapi.mlb.com`` (see CLAUDE.md).
Callers create a client with :func:`make_client` and pass it to the fetch
functions so a single connection pool is reused across parallel fetches.
"""

from typing import Any

import httpx

# Trailing slash matters: httpx joins base_url + path.lstrip("/"), so the base
# path must end in "/" and request paths below are relative (no leading slash).
BASE_URL = "https://statsapi.mlb.com/api/v1/"
_TIMEOUT = httpx.Timeout(10.0)


def make_client() -> httpx.AsyncClient:
    """Create an AsyncClient pointed at the MLB Stats API base URL."""
    return httpx.AsyncClient(base_url=BASE_URL, timeout=_TIMEOUT)


async def _get(
    client: httpx.AsyncClient, path: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    resp = await client.get(path, params=params)
    resp.raise_for_status()
    data: dict[str, Any] = resp.json()
    return data


async def get_person(client: httpx.AsyncClient, player_id: int) -> dict[str, Any]:
    """Fetch a player's biographical info: ``/people/{id}``.

    Hydrates ``currentTeam`` so the roster sync can derive the player's level
    (MLB/AAA/AA/…) from the team's sport — the bare response omits it.
    """
    return await _get(client, f"people/{player_id}", {"hydrate": "currentTeam"})


async def get_team(client: httpx.AsyncClient, team_id: int) -> dict[str, Any]:
    """Fetch a team: ``/teams/{id}``. Carries ``sport.id`` (1=MLB, 11-14=MiLB)."""
    return await _get(client, f"teams/{team_id}")


async def get_season_stats(
    client: httpx.AsyncClient,
    player_id: int,
    season: int,
    groups: tuple[str, ...] = ("hitting", "pitching"),
) -> dict[str, Any]:
    """Fetch a player's season totals: ``/people/{id}/stats?stats=season``."""
    params = {"stats": "season", "group": ",".join(groups), "season": season}
    return await _get(client, f"people/{player_id}/stats", params)


async def get_year_by_year(
    client: httpx.AsyncClient,
    player_id: int,
    groups: tuple[str, ...] = ("hitting", "pitching"),
    sport_id: int | None = None,
) -> dict[str, Any]:
    """Fetch per-season totals for every season: ``/people/{id}/stats?stats=yearByYear``.

    Without ``sport_id`` the API returns MLB seasons only; pass a MiLB sportId
    (11-14, 16) to get that level's seasons. A player who changed levels needs
    one call per level (the endpoint rejects a comma-joined list).
    """
    params: dict[str, Any] = {"stats": "yearByYear", "group": ",".join(groups)}
    if sport_id is not None:
        params["sportId"] = sport_id
    return await _get(client, f"people/{player_id}/stats", params)


async def get_schedule(
    client: httpx.AsyncClient, date: str, team_id: int | None = None, sport_id: int = 1
) -> dict[str, Any]:
    """Fetch games on a date: ``/schedule?sportId=&date=[&teamId=]``.

    ``date`` is ``YYYY-MM-DD``. ``sport_id`` 1 = MLB, 11/12/13/14 = MiLB levels.
    Omit ``team_id`` to get every game for the sport that day.
    """
    params: dict[str, Any] = {"sportId": sport_id, "date": date}
    if team_id is not None:
        params["teamId"] = team_id
    return await _get(client, "schedule", params)


async def get_boxscore(client: httpx.AsyncClient, game_pk: int) -> dict[str, Any]:
    """Fetch a game's boxscore: ``/game/{gamePk}/boxscore``."""
    return await _get(client, f"game/{game_pk}/boxscore")
