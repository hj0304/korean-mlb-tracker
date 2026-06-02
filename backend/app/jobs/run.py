"""CLI entrypoint for ETL jobs: ``python -m app.jobs.run --job=roster_sync``."""

import argparse
import asyncio

from app.jobs import roster_sync, season_stats

JOBS = {
    "roster_sync": roster_sync.run,
    "season_stats": season_stats.run,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an ETL job.")
    parser.add_argument("--job", required=True, choices=sorted(JOBS))
    args = parser.parse_args()
    asyncio.run(JOBS[args.job]())


if __name__ == "__main__":
    main()
