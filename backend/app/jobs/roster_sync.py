"""roster_sync: upsert the seed Korean players into the ``players`` table.

Fetches each seed player's bio (with ``currentTeam`` hydrated), then looks up
each team's sport to derive the player's level (MLB/AAA/AA/A+/A/R), and upserts
the rows.
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

# MLB Stats API sportId -> our level label (sportId map: see CLAUDE.md).
# 16 = Rookie (complex leagues), where several tracked prospects currently play.
_SPORT_ID_TO_LEVEL = {1: "MLB", 11: "AAA", 12: "AA", 13: "A+", 14: "A", 16: "R"}


def build_player_row(
    person: dict[str, Any], full_name_ko: str, level: str | None
) -> dict[str, Any]:
    """Map a ``/people/{id}`` person object to a ``players`` row.

    ``level`` is derived by the caller from the player's current team (see
    :func:`run`); the person object carries the team but not its sport.
    """
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
        "current_team_id": (person.get("currentTeam") or {}).get("id"),
        "current_level": level,
        "bats": person.get("batSide", {}).get("code"),
        "throws": person.get("pitchHand", {}).get("code"),
        "birth_date": date.fromisoformat(birth_date) if birth_date else None,
    }


async def run() -> None:
    async with mlb_client.make_client() as client:
        async with asyncio.TaskGroup() as tg:
            person_tasks: dict[int, asyncio.Task[dict[str, Any]]] = {
                player_id: tg.create_task(mlb_client.get_person(client, player_id))
                for player_id in KOREAN_PLAYERS
            }
        persons = {pid: task.result()["people"][0] for pid, task in person_tasks.items()}

        # Each player's level comes from their current team's sport, so fetch the
        # distinct teams once and map team id -> level.
        team_ids: set[int] = {
            team_id
            for p in persons.values()
            if (team_id := (p.get("currentTeam") or {}).get("id")) is not None
        }
        async with asyncio.TaskGroup() as tg:
            team_tasks = {
                team_id: tg.create_task(mlb_client.get_team(client, team_id))
                for team_id in team_ids
            }
        team_level = {
            team_id: _SPORT_ID_TO_LEVEL.get(task.result()["teams"][0]["sport"]["id"])
            for team_id, task in team_tasks.items()
        }

    rows = []
    for player_id, name_ko in KOREAN_PLAYERS.items():
        person = persons[player_id]
        team_id = (person.get("currentTeam") or {}).get("id")
        level = team_level.get(team_id) if team_id is not None else None
        rows.append(build_player_row(person, name_ko, level))

    stmt = pg_insert(Player).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={col: stmt.excluded[col] for col in _UPDATE_COLS} | {"updated_at": func.now()},
    )

    async with get_session_maker()() as session:
        await session.execute(stmt)
        await session.commit()

    print(f"roster_sync: upserted {len(rows)} players")
