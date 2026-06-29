"""season_stats: sync each tracked player's per-season totals into ``season_stats``.

Reads the roster from the ``players`` table, fetches every season (yearByYear)
from the MLB Stats API in parallel, transforms them, and upserts one row per
(season, stat group).

yearByYear is queried once per level (MLB + MiLB), because a tracked player may
have seasons at several levels (a prospect climbing, or an MLB player optioned
to AAA). The transformer merges those per-level responses per season.
"""

import asyncio
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import SPORT_ID_TO_LEVEL
from app.db.models import Player, SeasonStats
from app.db.session import get_session_maker
from app.services import mlb_client
from app.services.stats_transformer import transform_year_by_year

_SPORT_IDS = tuple(SPORT_ID_TO_LEVEL)  # (1, 11, 12, 13, 14, 16)


async def run() -> None:
    session_maker = get_session_maker()

    async with session_maker() as session:
        result = await session.execute(select(Player.id))
        player_ids = [pid for (pid,) in result.all()]

    async with mlb_client.make_client() as client:
        async with asyncio.TaskGroup() as tg:
            tasks: dict[tuple[int, int], asyncio.Task[dict[str, Any]]] = {
                (pid, sport_id): tg.create_task(
                    mlb_client.get_year_by_year(client, pid, sport_id=sport_id)
                )
                for pid in player_ids
                for sport_id in _SPORT_IDS
            }

    rows: list[dict[str, Any]] = []
    for pid in player_ids:
        payloads = [tasks[(pid, sport_id)].result() for sport_id in _SPORT_IDS]
        rows.extend(transform_year_by_year(payloads, pid))

    if not rows:
        print("season_stats: no stats to upsert")
        return

    stmt = pg_insert(SeasonStats).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["player_id", "season", "group_name", "level"],
        set_={
            "team_id": stmt.excluded.team_id,
            "stats": stmt.excluded.stats,
            "fetched_at": func.now(),
        },
    )

    async with session_maker() as session:
        await session.execute(stmt)
        await session.commit()

    print(f"season_stats: upserted {len(rows)} rows for {len(player_ids)} players")
