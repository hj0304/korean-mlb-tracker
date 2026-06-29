"""Pydantic DTOs for the players API."""

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict


class SeasonStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    season: int
    group_name: str
    level: str
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


class PlayerDetailOut(PlayerOut):
    """Player detail: summary plus bio and season totals."""

    bats: str | None
    throws: str | None
    birth_date: date | None
    season_stats: list[SeasonStatsOut]
