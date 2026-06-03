"""season_stats: sync each tracked player's per-season totals into ``season_stats``.

Reads the roster from the ``players`` table, fetches every season (yearByYear)
from the MLB Stats API in parallel, transforms them, and upserts one row per
(season, stat group).
"""

import asyncio
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.models import Player, SeasonStats
from app.db.session import get_session_maker
from app.services import mlb_client
from app.services.stats_transformer import transform_year_by_year


async def run() -> None:
    session_maker = get_session_maker()

    async with session_maker() as session:
        result = await session.execute(select(Player.id))
        player_ids = [pid for (pid,) in result.all()]

    async with mlb_client.make_client() as client:
        async with asyncio.TaskGroup() as tg:
            tasks: dict[int, asyncio.Task[dict[str, Any]]] = {
                pid: tg.create_task(mlb_client.get_year_by_year(client, pid)) for pid in player_ids
            }

    rows: list[dict[str, Any]] = []
    for pid in player_ids:
        rows.extend(transform_year_by_year(tasks[pid].result(), pid))

    if not rows:
        print("season_stats: no stats to upsert")
        return

    stmt = pg_insert(SeasonStats).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["player_id", "season", "group_name"],
        set_={"stats": stmt.excluded.stats, "fetched_at": func.now()},
    )

    async with session_maker() as session:
        await session.execute(stmt)
        await session.commit()

    print(f"season_stats: upserted {len(rows)} rows for {len(player_ids)} players")
