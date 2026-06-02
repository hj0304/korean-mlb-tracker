"""Transform MLB Stats API JSON into our DB-row shapes.

The most heavily tested module in the backend: every transformation has a
snapshot (golden-file) test in ``tests/test_stats_transformer.py`` driven by
real responses saved under ``tests/fixtures/mlb_responses/``.
"""

from typing import Any

# MLB boxscores label a batter's line "batting"; our schema and the season-stats
# endpoint both use "hitting". Normalize boxscore groups to ours.
_BOXSCORE_GROUP_TO_OURS = {"batting": "hitting", "pitching": "pitching"}


def transform_season_stats(payload: dict[str, Any], player_id: int) -> list[dict[str, Any]]:
    """Season-stats response -> ``season_stats`` rows, one per stat group.

    ``payload`` is the JSON from ``mlb_client.get_season_stats``. We take the
    first split per group (single-team season); multi-team stints are not
    modeled yet.
    """
    rows: list[dict[str, Any]] = []
    for group in payload.get("stats", []):
        splits = group.get("splits", [])
        if not splits:
            continue
        split = splits[0]
        rows.append(
            {
                "player_id": player_id,
                "season": int(split["season"]),
                "group_name": group["group"]["displayName"],
                "stats": split["stat"],
            }
        )
    return rows


def transform_game_log(
    boxscore: dict[str, Any], player_id: int, game_id: int, game_date: str
) -> list[dict[str, Any]]:
    """Boxscore response -> ``game_logs`` rows for one player, one per group played.

    Returns ``[]`` if the player didn't appear. ``game_id`` (gamePk) and
    ``game_date`` (``YYYY-MM-DD``) are passed in because the boxscore payload
    doesn't carry them.
    """
    teams = boxscore["teams"]
    key = f"ID{player_id}"
    for side, is_home in (("home", True), ("away", False)):
        if key not in teams[side]["players"]:
            continue
        opponent_id = teams["away" if is_home else "home"]["team"]["id"]
        player_stats = teams[side]["players"][key]["stats"]
        rows: list[dict[str, Any]] = []
        for box_group, our_group in _BOXSCORE_GROUP_TO_OURS.items():
            stat = player_stats.get(box_group)
            if not stat:
                continue
            rows.append(
                {
                    "player_id": player_id,
                    "game_id": game_id,
                    "game_date": game_date,
                    "opponent_id": opponent_id,
                    "is_home": is_home,
                    "group_name": our_group,
                    "stats": stat,
                }
            )
        return rows
    return []
