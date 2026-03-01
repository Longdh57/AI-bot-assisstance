"""create current_lists table

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "current_lists",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("list_id", sa.String(24), nullable=False),
        sa.UniqueConstraint("list_id", name="uq_current_lists_list_id"),
    )


def downgrade() -> None:
    op.drop_table("current_lists")
