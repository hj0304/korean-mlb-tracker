"""roster_sync: upsert the seed Korean players into the ``players`` table.

Fetches each seed player's bio from the MLB Stats API and upserts it. Team and
level (``current_team_id`` / ``current_level``) are left unset here and filled in
S2-01, where MiLB levels are handled.
"""

import asyncio
from datetime import date
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import KOREAN_PLAYERS
from app.db.models import Player
from app.db.session import get_session_maker
from app.services import mlb_client

# Columns refreshed on conflict (everything except the immutable id / created_at).
_UPDATE_COLS = (
    "full_name_en",
    "full_name_ko",
    "position",
    "player_type",
    "current_team_id",
    "current_level",
    "bats",
    "throws",
    "birth_date",
)


def build_player_row(person: dict[str, Any], full_name_ko: str) -> dict[str, Any]:
    """Map a ``/people/{id}`` person object to a ``players`` row."""
    position = person["primaryPosition"]
    if position["type"] == "Pitcher":
        player_type = "pitcher"
    elif position["abbreviation"] == "TWP":
        player_type = "two_way"
    else:
        player_type = "batter"

    birth_date = person.get("birthDate")
    return {
        "id": person["id"],
        "full_name_en": person["fullName"],
        "full_name_ko": full_name_ko,
        "position": position["abbreviation"],
        "player_type": player_type,
        "current_team_id": None,
        "current_level": None,
        "bats": person.get("batSide", {}).get("code"),
        "throws": person.get("pitchHand", {}).get("code"),
        "birth_date": date.fromisoformat(birth_date) if birth_date else None,
    }


async def run() -> None:
    async with mlb_client.make_client() as client:
        async with asyncio.TaskGroup() as tg:
            tasks: dict[int, asyncio.Task[dict[str, Any]]] = {
                player_id: tg.create_task(mlb_client.get_person(client, player_id))
                for player_id in KOREAN_PLAYERS
            }
    rows = [
        build_player_row(tasks[player_id].result()["people"][0], name_ko)
        for player_id, name_ko in KOREAN_PLAYERS.items()
    ]

    stmt = pg_insert(Player).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={col: stmt.excluded[col] for col in _UPDATE_COLS} | {"updated_at": func.now()},
    )

    async with get_session_maker()() as session:
        await session.execute(stmt)
        await session.commit()

    print(f"roster_sync: upserted {len(rows)} players")
