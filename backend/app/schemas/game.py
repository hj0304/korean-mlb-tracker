"""Pydantic DTOs for the game-logs API."""

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict


class GameLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_id: int
    game_date: date
    opponent_id: int | None
    is_home: bool | None
    group_name: str
    stats: dict[str, Any]
