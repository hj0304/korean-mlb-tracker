"""daily_games: sync tracked players' completed games for a date into ``game_logs``.

Fetches the day's MLB schedule, pulls the boxscore for each completed game, and
upserts one row per (player, game, stat group) for any tracked player who
appeared. Completed games only -- live/scheduled games are skipped (see CLAUDE.md).
"""

import asyncio
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import SPORT_ID_TO_LEVEL
from app.db.models import GameLog, Player
from app.db.session import get_session_maker
from app.services import mlb_client
from app.services.stats_transformer import transform_game_log


def extract_completed_games(
    schedule: dict[str, Any],
) -> list[tuple[int, str, frozenset[int]]]:
    """Schedule response -> ``(game_pk, official_date, team_ids)`` per completed game.

    ``team_ids`` are the home+away team ids, used by the caller to keep only
    games a tracked player's team played in (MiLB has hundreds of games a day).
    Skips anything not ``Final`` (live, scheduled, postponed).
    """
    games: list[tuple[int, str, frozenset[int]]] = []
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
            games.append((game["gamePk"], game["officialDate"], team_ids))
    return games


async def run(game_date: date | None = None) -> None:
    if game_date is None:
        game_date = date.today() - timedelta(days=1)
    date_str = game_date.isoformat()
    session_maker = get_session_maker()

    async with session_maker() as session:
        result = await session.execute(select(Player.id, Player.current_team_id))
        roster = result.all()
    player_ids = [pid for pid, _ in roster]
    team_ids = {tid for _, tid in roster if tid is not None}
    if not team_ids:
        print("daily_games: roster has no current teams; run roster_sync first")
        return

    async with mlb_client.make_client() as client:
        # MLB + every MiLB level, since tracked players span all of them.
        async with asyncio.TaskGroup() as tg:
            schedule_tasks = [
                tg.create_task(mlb_client.get_schedule(client, date_str, sport_id=sport_id))
                for sport_id in SPORT_ID_TO_LEVEL
            ]
        # Keep only completed games one of our teams played in.
        games = [
            (game_pk, official_date)
            for task in schedule_tasks
            for game_pk, official_date, game_team_ids in extract_completed_games(task.result())
            if game_team_ids & team_ids
        ]
        if not games:
            print(f"daily_games: no completed games for tracked teams on {date_str}")
            return
        async with asyncio.TaskGroup() as tg:
            boxscores = {
                game_pk: tg.create_task(mlb_client.get_boxscore(client, game_pk))
                for game_pk, _ in games
            }

    rows: list[dict[str, Any]] = []
    for game_pk, official_date in games:
        boxscore = boxscores[game_pk].result()
        game_day = date.fromisoformat(official_date)
        for pid in player_ids:
            for row in transform_game_log(boxscore, pid, game_pk, official_date):
                row["game_date"] = game_day  # Date column wants a date, not the ISO string
                rows.append(row)

    if not rows:
        print(f"daily_games: no tracked players appeared on {date_str}")
        return

    stmt = pg_insert(GameLog).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["player_id", "game_id", "group_name"],
        set_={"stats": stmt.excluded.stats, "fetched_at": func.now()},
    )

    async with session_maker() as session:
        await session.execute(stmt)
        await session.commit()

    print(f"daily_games: upserted {len(rows)} rows for {len(player_ids)} players on {date_str}")
