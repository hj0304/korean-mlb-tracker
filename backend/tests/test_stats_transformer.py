import json
from pathlib import Path
from typing import Any

from app.services import stats_transformer

FIXTURES = Path(__file__).parent / "fixtures" / "mlb_responses"
SNAPSHOTS = Path(__file__).parent / "fixtures" / "snapshots"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def test_transform_season_stats_snapshot() -> None:
    payload = _load(FIXTURES / "season_hitting_kim_2026.json")
    result = stats_transformer.transform_season_stats(payload, player_id=808975)
    assert result == _load(SNAPSHOTS / "season_hitting_kim_2026.json")


def test_transform_game_log_snapshot() -> None:
    box = _load(FIXTURES / "boxscore_822832.json")
    result = stats_transformer.transform_game_log(
        box, player_id=808975, game_id=822832, game_date="2026-04-06"
    )
    assert result == _load(SNAPSHOTS / "game_log_kim_822832.json")


def test_transform_game_log_player_absent() -> None:
    box = _load(FIXTURES / "boxscore_822832.json")
    # A player who didn't appear in this game yields no rows.
    assert (
        stats_transformer.transform_game_log(
            box, player_id=1, game_id=822832, game_date="2026-04-06"
        )
        == []
    )
