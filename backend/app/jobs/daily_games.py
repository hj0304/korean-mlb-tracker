"""daily_games: sync tracked players' completed games for a date into ``game_logs``.

Fetches the day's MLB schedule, pulls the boxscore for each completed game, and
upserts one row per (player, game, stat group) for any tracked player who
appeared. Completed games only -- live/scheduled games are skipped (see CLAUDE.md).
"""

import asyncio
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import SPORT_ID_TO_LEVEL
from app.db.models import GameLog, Player, SeasonStats
from app.db.session import get_session_maker
from app.services import mlb_client
from app.services.stats_transformer import transform_game_log

# Korea has had no DST since 1988 and is permanently UTC+9, so a fixed offset is
# correct and avoids depending on a system tz database (absent on Windows).
_KST = timezone(timedelta(hours=9))


def extract_completed_games(
    schedule: dict[str, Any],
) -> list[tuple[int, date, frozenset[int]]]:
    """Schedule response -> ``(game_pk, game_date, team_ids)`` per completed game.

    ``game_date`` is the game's calendar date in KST, derived from the UTC
    ``gameDate`` timestamp -- a US night game falls on the next day in Korea,
    and that's the date our (Korean) users expect. (The API's ``officialDate``
    is the venue-local US date, which lags one day behind KST.)

    ``team_ids`` are the home+away team ids, used by the caller to keep only
    games a tracked player's team played in (MiLB has hundreds of games a day).
    Skips anything not ``Final`` (live, scheduled, postponed).
    """
    games: list[tuple[int, date, frozenset[int]]] = []
    for day in schedule.get("dates", []):
        for game in day.get("games", []):
            if game["status"]["abstractGameState"] != "Final":
                continue
            teams = game.get("teams", {})
            team_ids = frozenset(
                teams[side]["team"]["id"]
                for side in ("home", "away")
                if (teams.get(side) or {}).get("team", {}).get("id") is not None
            )
            game_date = datetime.fromisoformat(game["gameDate"]).astimezone(_KST).date()
            games.append((game["gamePk"], game_date, team_ids))
    return games


async def run(game_date: date | None = None) -> None:
    if game_date is None:
        game_date = date.today() - timedelta(days=1)
    date_str = game_date.isoformat()
    session_maker = get_session_maker()

    async with session_maker() as session:
        result = await session.execute(select(Player.id, Player.current_team_id))
        roster = result.all()
        # Also every team a tracked player has appeared for this season, not just
        # their current one: a player optioned/promoted mid-season plays for a team
        # that isn't current_team_id, and filtering on current alone would skip
        # those games (current_team_id only refreshes when roster_sync runs).
        season_team_ids = await session.execute(select(SeasonStats.team_id).distinct())
    player_ids = [pid for pid, _ in roster]
    team_ids = {tid for _, tid in roster if tid is not None}
    team_ids |= {tid for (tid,) in season_team_ids.all() if tid is not None}
    if not team_ids:
        print("daily_games: roster has no current teams; run roster_sync first")
        return

    async with mlb_client.make_client() as client:
        # MLB + every MiLB level, since tracked players span all of them.
        async with asyncio.TaskGroup() as tg:
            schedule_tasks = {
                sport_id: tg.create_task(
                    mlb_client.get_schedule(client, date_str, sport_id=sport_id)
                )
                for sport_id in SPORT_ID_TO_LEVEL
            }
        # Keep only completed games one of our teams played in, tagged with the
        # level of the schedule they came from.
        games = [
            (game_pk, game_day, SPORT_ID_TO_LEVEL[sport_id])
            for sport_id, task in schedule_tasks.items()
            for game_pk, game_day, game_team_ids in extract_completed_games(task.result())
            if game_team_ids & team_ids
        ]
        if not games:
            print(f"daily_games: no completed games for tracked teams on {date_str}")
            return
        async with asyncio.TaskGroup() as tg:
            boxscores = {
                game_pk: tg.create_task(mlb_client.get_boxscore(client, game_pk))
                for game_pk, _, _ in games
            }

    rows: list[dict[str, Any]] = []
    for game_pk, game_day, level in games:
        boxscore = boxscores[game_pk].result()
        for pid in player_ids:
            for row in transform_game_log(boxscore, pid, game_pk, game_day.isoformat(), level):
                row["game_date"] = game_day  # Date column wants a date, not the ISO string
                rows.append(row)

    if not rows:
        print(f"daily_games: no tracked players appeared on {date_str}")
        return

    stmt = pg_insert(GameLog).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["player_id", "game_id", "group_name"],
        set_={
            "game_date": stmt.excluded.game_date,
            "stats": stmt.excluded.stats,
            "fetched_at": func.now(),
        },
    )

    async with session_maker() as session:
        await session.execute(stmt)
        await session.commit()

    print(f"daily_games: upserted {len(rows)} rows for {len(player_ids)} players on {date_str}")
