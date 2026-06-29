"""add level dimension to season_stats and game_logs

Splits stats by league level (MLB/AAA/AA/A+/A/R):
- ``season_stats`` gains ``level`` as part of the primary key, so a player who
  played at several levels in one season keeps a row per level (previously only
  the level with the most games survived).
- ``game_logs`` gains a nullable ``level`` column.

Backfill: season_stats reuses the level already stashed in ``stats->>'level'``
(defaulting to MLB if absent); game_logs derives each game's level from the
opponent team's level (the opponent is at the same level as the game). The
season_stats backfill only seeds one level per (season, group) — a full
per-level rebuild requires re-running the season_stats ETL after this migration.

Revision ID: b8e1c2a3d4f5
Revises: f4a42d6d7297
Create Date: 2026-06-29 19:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b8e1c2a3d4f5"
down_revision: Union[str, Sequence[str], None] = "f4a42d6d7297"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # season_stats: add level, backfill, fold into the primary key.
    op.add_column("season_stats", sa.Column("level", sa.Text(), nullable=True))
    op.execute("UPDATE season_stats SET level = COALESCE(stats->>'level', 'MLB')")
    op.alter_column("season_stats", "level", nullable=False)
    op.drop_constraint("season_stats_pkey", "season_stats", type_="primary")
    op.create_primary_key(
        "season_stats_pkey", "season_stats", ["player_id", "season", "group_name", "level"]
    )

    # game_logs: add level, backfill from the opponent team's level.
    op.add_column("game_logs", sa.Column("level", sa.Text(), nullable=True))
    op.execute("UPDATE game_logs gl SET level = t.level FROM teams t WHERE t.id = gl.opponent_id")


def downgrade() -> None:
    op.drop_column("game_logs", "level")
    op.drop_constraint("season_stats_pkey", "season_stats", type_="primary")
    op.create_primary_key(
        "season_stats_pkey", "season_stats", ["player_id", "season", "group_name"]
    )
    op.drop_column("season_stats", "level")
