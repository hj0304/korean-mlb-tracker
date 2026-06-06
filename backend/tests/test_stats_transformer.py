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


def test_transform_year_by_year_snapshot() -> None:
    payload = _load(FIXTURES / "yearbyyear_kim_hs.json")
    result = stats_transformer.transform_year_by_year([payload], player_id=673490)
    assert result == _load(SNAPSHOTS / "yearbyyear_kim_hs.json")


def test_transform_year_by_year_combines_multi_team_season() -> None:
    payload = _load(FIXTURES / "yearbyyear_kim_hs.json")
    rows = stats_transformer.transform_year_by_year([payload], player_id=673490)
    # one row per season (2021-2026), even though 2025 was split across two teams
    assert sorted(r["season"] for r in rows) == [2021, 2022, 2023, 2024, 2025, 2026]
    # 2025 uses the combined numTeams total (.234 / 48 G), not a single team's split
    y2025 = next(r for r in rows if r["season"] == 2025)
    assert y2025["stats"]["avg"] == ".234"
    assert y2025["stats"]["gamesPlayed"] == 48
    # MLB seasons are labelled with their level
    assert y2025["stats"]["level"] == "MLB"


def test_transform_year_by_year_merges_levels_by_games() -> None:
    """A player at MLB + AAA in the same seasons: each season keeps the level
    where he played the most games."""
    mlb = _load(FIXTURES / "yearbyyear_bae_mlb.json")
    aaa = _load(FIXTURES / "yearbyyear_bae_aaa.json")
    rows = stats_transformer.transform_year_by_year([mlb, aaa], player_id=678225)
    by_season = {r["season"]: r["stats"] for r in rows}
    # 2023: 111 MLB G beats 9 AAA G -> MLB
    assert by_season[2023]["level"] == "MLB"
    assert by_season[2023]["avg"] == ".231"
    # 2025: 67 AAA G beats 13 MLB G -> AAA
    assert by_season[2025]["level"] == "AAA"
    assert by_season[2025]["avg"] == ".292"
    # 2026: AAA only
    assert by_season[2026]["level"] == "AAA"


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
