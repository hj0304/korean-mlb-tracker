"""Players API tests with a stubbed DB session (no Postgres needed).

Real Postgres integration tests come in S1-10 (testcontainers); here we override
the session dependency to verify routing, ORM->Pydantic serialization, and the
404 path in isolation.
"""

from collections.abc import AsyncGenerator, Sequence
from datetime import date
from typing import Any

from fastapi.testclient import TestClient

from app.api.deps import get_session
from app.db.models import GameLog, Player, SeasonStats
from app.main import app


def _player(**overrides: Any) -> Player:
    fields: dict[str, Any] = {
        "id": 808975,
        "full_name_en": "Hyeseong Kim",
        "full_name_ko": "김혜성",
        "position": "SS",
        "player_type": "batter",
        "current_team_id": 119,
        "current_level": "MLB",
        "is_active": True,
        "bats": "L",
        "throws": "R",
        "birth_date": date(1999, 1, 27),
    }
    fields.update(overrides)
    return Player(**fields)


class _Scalars:
    def __init__(self, items: Sequence[Any]) -> None:
        self._items = items

    def all(self) -> Sequence[Any]:
        return self._items


class _Result:
    def __init__(self, items: Sequence[Any]) -> None:
        self._items = items

    def scalars(self) -> _Scalars:
        return _Scalars(self._items)


class _FakeSession:
    """Stub: execute() returns canned rows; get() returns a canned object.

    Each endpoint uses execute() for a single query, so no statement
    inspection is needed.
    """

    def __init__(self, execute_items: Sequence[Any] = (), get_result: Any = None) -> None:
        self._execute_items = execute_items
        self._get_result = get_result

    async def execute(self, *args: Any, **kwargs: Any) -> _Result:
        return _Result(list(self._execute_items))

    async def get(self, *args: Any, **kwargs: Any) -> Any:
        return self._get_result


def _use(session: _FakeSession) -> None:
    async def _dep() -> AsyncGenerator[Any, None]:
        yield session

    app.dependency_overrides[get_session] = _dep


def test_list_players() -> None:
    _use(_FakeSession(execute_items=[_player()]))
    try:
        r = TestClient(app).get("/api/v1/players")
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    body = r.json()
    assert body[0]["id"] == 808975
    assert body[0]["full_name_ko"] == "김혜성"
    # detail-only fields must not leak into the list schema
    assert "season_stats" not in body[0]


def test_get_player_detail() -> None:
    stats = SeasonStats(
        player_id=808975,
        season=2026,
        group_name="hitting",
        stats={"avg": ".300", "homeRuns": 5},
    )
    _use(_FakeSession(execute_items=[stats], get_result=_player()))
    try:
        r = TestClient(app).get("/api/v1/players/808975")
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    body = r.json()
    assert body["full_name_ko"] == "김혜성"
    assert body["birth_date"] == "1999-01-27"
    assert body["season_stats"][0]["group_name"] == "hitting"
    assert body["season_stats"][0]["stats"]["homeRuns"] == 5


def test_get_player_not_found() -> None:
    _use(_FakeSession(get_result=None))
    try:
        r = TestClient(app).get("/api/v1/players/999")
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 404


def test_list_player_games() -> None:
    log = GameLog(
        player_id=808975,
        game_id=822832,
        game_date=date(2026, 4, 6),
        opponent_id=141,
        is_home=False,
        group_name="hitting",
        stats={"hits": 2, "homeRuns": 1},
    )
    _use(_FakeSession(execute_items=[log]))
    try:
        r = TestClient(app).get("/api/v1/players/808975/games")
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    body = r.json()
    assert body[0]["game_id"] == 822832
    assert body[0]["game_date"] == "2026-04-06"
    assert body[0]["is_home"] is False
    assert body[0]["stats"]["homeRuns"] == 1


def test_list_player_games_empty_with_since() -> None:
    _use(_FakeSession(execute_items=[]))
    try:
        r = TestClient(app).get("/api/v1/players/808975/games?since=2026-05-01")
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    assert r.json() == []
