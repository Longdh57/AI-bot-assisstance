"""create cards table

Revision ID: 0001
Revises:
Create Date: 2026-03-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cards",
        sa.Column("id", sa.String(24), primary_key=True),

        # Board / list references
        sa.Column("id_short", sa.Integer(), nullable=False),
        sa.Column("id_board", sa.String(24), nullable=False),
        sa.Column("id_list", sa.String(24), nullable=False),
        sa.Column("id_attachment_cover", sa.String(24), nullable=True),
        sa.Column("mirror_source_id", sa.String(24), nullable=True),

        # Identity
        sa.Column("name", sa.String(1000), nullable=False),
        sa.Column("short_link", sa.String(100), nullable=False),
        sa.Column("short_url", sa.String(500), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),

        # Content
        sa.Column("desc", sa.Text(), nullable=False),
        sa.Column("desc_data", sa.JSON(), nullable=False),

        # State
        sa.Column("closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("subscribed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("manual_cover_attachment", sa.Boolean(), nullable=False, server_default=sa.false()),

        # Dates
        sa.Column("date_last_activity", sa.DateTime(), nullable=False),
        sa.Column("due", sa.Date(), nullable=True),
        sa.Column("due_reminder", sa.String(50), nullable=True),

        # Location
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("location_name", sa.String(500), nullable=True),
        sa.Column("coordinates", sa.String(100), nullable=True),

        # Position
        sa.Column("pos", sa.Float(), nullable=False, server_default="0"),

        # Role & creation
        sa.Column(
            "card_role",
            sa.Enum("separator", "board", "mirror", "link", name="card_role_enum"),
            nullable=True,
        ),
        sa.Column("creation_method", sa.String(100), nullable=True),

        # Relations (JSON arrays of Trello IDs)
        sa.Column("id_members", sa.JSON(), nullable=False),
        sa.Column("id_members_voted", sa.JSON(), nullable=False),
        sa.Column("id_checklists", sa.JSON(), nullable=False),
        sa.Column("id_labels", sa.JSON(), nullable=False),
        sa.Column("labels", sa.JSON(), nullable=False),
        sa.Column("check_item_states", sa.JSON(), nullable=False),

        # Rich sub-objects (JSON)
        sa.Column("badges", sa.JSON(), nullable=False),
        sa.Column("cover", sa.JSON(), nullable=False),
        sa.Column("limits", sa.JSON(), nullable=False),
    )
    op.create_index("ix_cards_id_board", "cards", ["id_board"])
    op.create_index("ix_cards_id_list", "cards", ["id_list"])


def downgrade() -> None:
    op.drop_index("ix_cards_id_list", table_name="cards")
    op.drop_index("ix_cards_id_board", table_name="cards")
    op.drop_table("cards")
    op.execute("DROP TYPE IF EXISTS card_role_enum")
