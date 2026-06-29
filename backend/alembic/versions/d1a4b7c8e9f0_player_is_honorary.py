"""add is_honorary to players

Flags "명예 한국인" players (not Korean-born, but represented Team Korea
internationally) so the UI can label and filter them apart from Korean nationals.
Defaults false; roster_sync sets it from the HONORARY_PLAYERS seed.

Revision ID: d1a4b7c8e9f0
Revises: c9f2d3e4a5b6
Create Date: 2026-06-30 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1a4b7c8e9f0"
down_revision: Union[str, Sequence[str], None] = "c9f2d3e4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "players",
        sa.Column("is_honorary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("players", "is_honorary")
