"""create trello_lists table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trello_lists",
        sa.Column("id", sa.String(24), primary_key=True),
        sa.Column("id_board", sa.String(24), nullable=False),
        sa.Column("name", sa.String(1000), nullable=False),
        sa.Column("closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("subscribed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("pos", sa.Float(), nullable=False, server_default="0"),
        sa.Column("soft_limit", sa.String(100), nullable=True),
        sa.Column("limits", sa.JSON(), nullable=False),
    )
    op.create_index("ix_trello_lists_id_board", "trello_lists", ["id_board"])


def downgrade() -> None:
    op.drop_index("ix_trello_lists_id_board", table_name="trello_lists")
    op.drop_table("trello_lists")
