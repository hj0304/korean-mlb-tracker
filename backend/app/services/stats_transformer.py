"""Transform MLB Stats API JSON into our DB-row shapes.

The most heavily tested module in the backend: every transformation has a
snapshot (golden-file) test in ``tests/test_stats_transformer.py`` driven by
real responses saved under ``tests/fixtures/mlb_responses/``.
"""

from typing import Any

from app.core.config import SPORT_ID_TO_LEVEL

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


def transform_year_by_year(payloads: list[dict[str, Any]], player_id: int) -> list[dict[str, Any]]:
    """yearByYear responses -> ``season_stats`` rows, one per (season, group, level).

    Takes one payload per level (see ``mlb_client.get_year_by_year``). A player
    can appear at several levels in one season (a prospect promoted, or an MLB
    player optioned to AAA) and across multiple teams within a level (the API
    adds a combined ``numTeams`` split). Each level is kept as its own row;
    within a level, the split with the most ``gamesPlayed`` wins, which picks the
    combined total over its per-team components. Splits whose sport isn't a
    tracked level are skipped. The level (MLB/AAA/…) is a column on the row.
    """
    # (season, group_name, level) -> (games_played, stats)
    best: dict[tuple[int, str, str], tuple[int, dict[str, Any]]] = {}
    for payload in payloads:
        for group in payload.get("stats", []):
            group_name = group["group"]["displayName"]
            for split in group.get("splits", []):
                level = SPORT_ID_TO_LEVEL.get(split.get("sport", {}).get("id"))
                if level is None:
                    continue
                season = int(split["season"])
                stat = split["stat"]
                games = int(stat.get("gamesPlayed") or 0)
                key = (season, group_name, level)
                if key not in best or games > best[key][0]:
                    best[key] = (games, stat)
    return [
        {
            "player_id": player_id,
            "season": season,
            "group_name": group_name,
            "level": level,
            "stats": stats,
        }
        for (season, group_name, level), (_, stats) in best.items()
    ]


def transform_game_log(
    boxscore: dict[str, Any], player_id: int, game_id: int, game_date: str, level: str | None
) -> list[dict[str, Any]]:
    """Boxscore response -> ``game_logs`` rows for one player, one per group played.

    Returns ``[]`` if the player didn't appear. ``game_id`` (gamePk),
    ``game_date`` (``YYYY-MM-DD``) and ``level`` (MLB/AAA/…) are passed in because
    the boxscore payload doesn't carry them — the caller knows them from the
    schedule it fetched the game from.
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
                    "level": level,
                    "group_name": our_group,
                    "stats": stat,
                }
            )
        return rows
    return []
