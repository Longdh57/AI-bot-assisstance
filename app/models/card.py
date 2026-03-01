from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Card(Base):
    """SQLAlchemy ORM model representing a Trello Card cloned from the Trello API."""

    __tablename__ = "cards"

    # Primary key — Trello's 24-char hex ID
    id: Mapped[str] = mapped_column(String(24), primary_key=True)

    # Board / list references
    id_short: Mapped[int] = mapped_column(Integer, nullable=False)
    id_board: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    id_list: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    id_attachment_cover: Mapped[str | None] = mapped_column(String(24), nullable=True)
    mirror_source_id: Mapped[str | None] = mapped_column(String(24), nullable=True)

    # Identity
    name: Mapped[str] = mapped_column(String(1000), nullable=False)
    short_link: Mapped[str] = mapped_column(String(100), nullable=False)
    short_url: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Content
    desc: Mapped[str] = mapped_column(Text, nullable=False, default="")
    desc_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # State
    closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    subscribed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    manual_cover_attachment: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Dates
    date_last_activity: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    due: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_reminder: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Location
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    coordinates: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Position
    pos: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Role & creation
    card_role: Mapped[str | None] = mapped_column(
        Enum("separator", "board", "mirror", "link", name="card_role_enum"),
        nullable=True,
    )
    creation_method: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relations stored as JSON arrays of Trello IDs
    id_members: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    id_members_voted: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    id_checklists: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    id_labels: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    labels: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    check_item_states: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Rich sub-objects stored as JSON
    badges: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    cover: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    limits: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
