import json
from datetime import date
from pathlib import Path
from typing import Any

from app.jobs import roster_sync

FIXTURES = Path(__file__).parent / "fixtures" / "mlb_responses"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def test_build_player_row() -> None:
    person = _load(FIXTURES / "person_kim.json")["people"][0]
    assert roster_sync.build_player_row(person, "김혜성", "MLB") == {
        "id": 808975,
        "full_name_en": "Hyeseong Kim",
        "full_name_ko": "김혜성",
        "position": "SS",
        "player_type": "batter",
        "current_team_id": None,
        "current_level": "MLB",
        "bats": "L",
        "throws": "R",
        "birth_date": date(1999, 1, 27),
    }


def test_build_player_row_milb_with_team() -> None:
    """MiLB pitcher with a hydrated currentTeam: team id and level flow through."""
    person = _load(FIXTURES / "person_um.json")["people"][0]
    row = roster_sync.build_player_row(person, "엄형찬", "A")
    assert row["id"] == 805870
    assert row["full_name_ko"] == "엄형찬"
    assert row["player_type"] == "batter"  # catcher
    assert row["current_team_id"] == 3705
    assert row["current_level"] == "A"


def test_sport_id_to_level_mapping() -> None:
    from app.core.config import SPORT_ID_TO_LEVEL

    assert SPORT_ID_TO_LEVEL[1] == "MLB"
    assert SPORT_ID_TO_LEVEL[14] == "A"
