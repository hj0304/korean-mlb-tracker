"""Pydantic DTOs for the players API."""

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict


class SeasonStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    season: int
    group_name: str
    level: str
    team_id: int | None = None
    team_name: str | None = None
    team_abbrev: str | None = None
    stats: dict[str, Any]


class PlayerOut(BaseModel):
    """Player summary for the list endpoint / cards."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name_en: str
    full_name_ko: str
    position: str
    player_type: str
    current_team_id: int | None
    current_level: str | None
    is_active: bool
    is_honorary: bool


class PlayerDetailOut(PlayerOut):
    """Player detail: summary plus bio and season totals."""

    bats: str | None
    throws: str | None
    birth_date: date | None
    current_team_name: str | None = None
    current_team_abbrev: str | None = None
    season_stats: list[SeasonStatsOut]
