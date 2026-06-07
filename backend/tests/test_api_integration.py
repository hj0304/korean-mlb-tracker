"""End-to-end API tests against a real Postgres (testcontainers).

Skips when Docker is unavailable (see ``conftest.pg_url``).
"""

from httpx import AsyncClient


async def test_players_api_end_to_end(seeded_client: AsyncClient) -> None:
    # list
    r = await seeded_client.get("/api/v1/players")
    assert r.status_code == 200
    assert any(p["id"] == 808975 for p in r.json())

    # list filtered by level (S2-02)
    r = await seeded_client.get("/api/v1/players?level=MLB")
    assert r.status_code == 200
    assert [p["id"] for p in r.json()] == [808975]
    r = await seeded_client.get("/api/v1/players?level=AAA")
    assert r.status_code == 200
    assert r.json() == []

    # detail: bio + season totals
    r = await seeded_client.get("/api/v1/players/808975")
    assert r.status_code == 200
    detail = r.json()
    assert detail["full_name_ko"] == "김혜성"
    assert detail["birth_date"] == "1999-01-27"
    assert detail["season_stats"][0]["group_name"] == "hitting"
    assert detail["season_stats"][0]["stats"]["homeRuns"] == 5

    # games: newest first
    r = await seeded_client.get("/api/v1/players/808975/games")
    assert r.status_code == 200
    games = r.json()
    assert len(games) == 2
    assert games[0]["game_date"] == "2026-05-10"

    # games: since filter
    r = await seeded_client.get("/api/v1/players/808975/games?since=2026-05-01")
    assert r.status_code == 200
    filtered = r.json()
    assert len(filtered) == 1
    assert filtered[0]["game_id"] == 823999

    # missing player
    r = await seeded_client.get("/api/v1/players/999999")
    assert r.status_code == 404

    # dashboard: latest game day's feed (S2-03)
    r = await seeded_client.get("/api/v1/dashboard/today")
    assert r.status_code == 200
    dash = r.json()
    assert dash["date"] == "2026-05-10"  # newest of the two seeded games
    assert len(dash["games"]) == 1
    g = dash["games"][0]
    assert g["player_id"] == 808975
    assert g["full_name_ko"] == "김혜성"
    assert g["current_level"] == "MLB"
    assert g["stats"]["hits"] == 1
