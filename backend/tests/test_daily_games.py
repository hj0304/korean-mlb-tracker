import json
from datetime import date
from pathlib import Path
from typing import Any

from app.jobs import daily_games

FIXTURES = Path(__file__).parent / "fixtures" / "mlb_responses"


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_extract_completed_games() -> None:
    schedule = _load("schedule_2026-04-06.json")
    games = daily_games.extract_completed_games(schedule)
    assert len(games) == 13
    # gameDate 2026-04-06T23:07:00Z (US night) is 2026-04-07 in KST.
    assert (822832, date(2026, 4, 7)) in {(pk, d) for pk, d, _ in games}
    assert all(isinstance(pk, int) and isinstance(d, date) for pk, d, _ in games)


def test_extract_completed_games_captures_team_ids() -> None:
    schedule = _load("schedule_2026-04-06.json")
    by_pk = {pk: team_ids for pk, _, team_ids in daily_games.extract_completed_games(schedule)}
    # home Rays (139) vs away (112) — used to filter to tracked teams
    assert by_pk[823002] == frozenset({139, 112})


def test_extract_completed_games_skips_unfinished() -> None:
    schedule = {
        "dates": [
            {
                "games": [
                    {
                        "gamePk": 1,
                        "gameDate": "2026-04-06T23:07:00Z",
                        "status": {"abstractGameState": "Final"},
                        "teams": {
                            "home": {"team": {"id": 10}},
                            "away": {"team": {"id": 20}},
                        },
                    },
                    {
                        "gamePk": 2,
                        "gameDate": "2026-04-06T23:07:00Z",
                        "status": {"abstractGameState": "Live"},
                    },
                    {
                        "gamePk": 3,
                        "gameDate": "2026-04-06T23:07:00Z",
                        "status": {"abstractGameState": "Preview"},
                    },
                ]
            }
        ]
    }
    assert daily_games.extract_completed_games(schedule) == [
        (1, date(2026, 4, 7), frozenset({10, 20}))
    ]
