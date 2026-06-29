"""Pydantic DTOs for the dashboard API."""

from datetime import date
from typing import Any

from pydantic import BaseModel


class DashboardGameOut(BaseModel):
    """One tracked player's line in the latest game day's feed (player + game)."""

    player_id: int
    full_name_ko: str
    full_name_en: str
    current_level: str | None
    player_type: str
    opponent_id: int | None
    opponent_name: str | None = None
    opponent_abbrev: str | None = None
    is_home: bool | None
    group_name: str
    stats: dict[str, Any]


class DashboardOut(BaseModel):
    """Latest game day plus every tracked player who appeared that day.

    ``date`` is null when there are no game logs at all.
    """

    date: date | None
    games: list[DashboardGameOut]
