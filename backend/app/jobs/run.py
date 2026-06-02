"""CLI entrypoint for ETL jobs: ``python -m app.jobs.run --job=roster_sync``."""

import argparse
import asyncio
from datetime import date

from app.jobs import daily_games, roster_sync, season_stats

JOBS = {
    "roster_sync": roster_sync.run,
    "season_stats": season_stats.run,
    "daily_games": daily_games.run,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an ETL job.")
    parser.add_argument("--job", required=True, choices=sorted(JOBS))
    parser.add_argument("--date", help="YYYY-MM-DD for daily_games (default: yesterday)")
    args = parser.parse_args()

    if args.job == "daily_games":
        game_date = date.fromisoformat(args.date) if args.date else None
        asyncio.run(daily_games.run(game_date))
    else:
        asyncio.run(JOBS[args.job]())


if __name__ == "__main__":
    main()
