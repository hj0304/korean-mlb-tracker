"""add team_id to season_stats

Records which team a player was on for each (season, level) row, so the career
table can show a per-season team column. Nullable: a multi-team season collapses
to the combined ``numTeams`` split, which carries no single team. Populated by
re-running the season_stats ETL (the transformer reads team from each split).

Revision ID: c9f2d3e4a5b6
Revises: b8e1c2a3d4f5
Create Date: 2026-06-29 15:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9f2d3e4a5b6"
down_revision: Union[str, Sequence[str], None] = "b8e1c2a3d4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("season_stats", sa.Column("team_id", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("season_stats", "team_id")
