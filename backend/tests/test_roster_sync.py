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
    assert roster_sync.build_player_row(person, "김혜성") == {
        "id": 808975,
        "full_name_en": "Hyeseong Kim",
        "full_name_ko": "김혜성",
        "position": "SS",
        "player_type": "batter",
        "current_team_id": None,
        "current_level": None,
        "bats": "L",
        "throws": "R",
        "birth_date": date(1999, 1, 27),
    }
