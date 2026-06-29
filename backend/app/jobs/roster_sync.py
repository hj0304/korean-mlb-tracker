"""roster_sync: upsert the seed Korean players into the ``players`` table.

Fetches each seed player's bio (with ``currentTeam`` hydrated) plus every team
at each tracked level, uses the team's sport to derive the player's level
(MLB/AAA/AA/A+/A/R), and upserts both the players and the teams (so game logs
can render opponent ids as names).
"""

import asyncio
from datetime import date
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import HONORARY_PLAYERS, KOREAN_PLAYERS, SPORT_ID_TO_LEVEL
from app.db.models import Player, Team
from app.db.session import get_session_maker
from app.services import mlb_client

# Seed roster: id -> (Korean name, is_honorary). Korean nationals + "명예 한국인".
_SEED: dict[int, tuple[str, bool]] = {
    **{pid: (name, False) for pid, name in KOREAN_PLAYERS.items()},
    **{pid: (name, True) for pid, name in HONORARY_PLAYERS.items()},
}

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
    "is_honorary",
)

# MLB league id -> our short code; every other league is minor-league.
_LEAGUE_CODE = {103: "AL", 104: "NL"}


def build_player_row(
    person: dict[str, Any], full_name_ko: str, level: str | None, is_honorary: bool = False
) -> dict[str, Any]:
    """Map a ``/people/{id}`` person object to a ``players`` row.

    ``level`` is derived by the caller from the player's current team (see
    :func:`run`); the person object carries the team but not its sport.
    ``is_honorary`` marks "명예 한국인" players (see ``HONORARY_PLAYERS``).
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
        "is_honorary": is_honorary,
    }


def build_team_row(team: dict[str, Any]) -> dict[str, Any]:
    """Map a ``/teams`` team object to a ``teams`` row."""
    return {
        "id": team["id"],
        "name": team["name"],
        "abbrev": team.get("abbreviation") or team["name"],
        "league": _LEAGUE_CODE.get(team.get("league", {}).get("id"), "MiLB"),
        "level": SPORT_ID_TO_LEVEL.get(team.get("sport", {}).get("id")),
    }


async def run() -> None:
    async with mlb_client.make_client() as client:
        async with asyncio.TaskGroup() as tg:
            person_tasks: dict[int, asyncio.Task[dict[str, Any]]] = {
                player_id: tg.create_task(mlb_client.get_person(client, player_id))
                for player_id in _SEED
            }
            # Every team at each tracked level, used both to populate the teams
            # table and to derive each player's level from their team's sport.
            teams_tasks = {
                sport_id: tg.create_task(mlb_client.get_teams(client, sport_id))
                for sport_id in SPORT_ID_TO_LEVEL
            }
        persons = {pid: task.result()["people"][0] for pid, task in person_tasks.items()}
        teams_by_id = {
            team["id"]: team for task in teams_tasks.values() for team in task.result()["teams"]
        }

    team_rows = [build_team_row(team) for team in teams_by_id.values()]

    player_rows = []
    for player_id, (name_ko, is_honorary) in _SEED.items():
        person = persons[player_id]
        team_id = (person.get("currentTeam") or {}).get("id")
        team = teams_by_id.get(team_id) if team_id is not None else None
        level = SPORT_ID_TO_LEVEL.get(team.get("sport", {}).get("id")) if team else None
        player_rows.append(build_player_row(person, name_ko, level, is_honorary))

    team_stmt = pg_insert(Team).values(team_rows)
    team_stmt = team_stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={col: team_stmt.excluded[col] for col in ("name", "abbrev", "league", "level")},
    )

    player_stmt = pg_insert(Player).values(player_rows)
    player_stmt = player_stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={col: player_stmt.excluded[col] for col in _UPDATE_COLS} | {"updated_at": func.now()},
    )

    async with get_session_maker()() as session:
        await session.execute(team_stmt)
        await session.execute(player_stmt)
        await session.commit()

    print(f"roster_sync: upserted {len(player_rows)} players, {len(team_rows)} teams")
