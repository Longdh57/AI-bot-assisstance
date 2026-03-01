from sqlalchemy import JSON, Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TrelloList(Base):
    """SQLAlchemy ORM model representing a Trello List cloned from the Trello API."""

    __tablename__ = "trello_lists"

    # Primary key — Trello's 24-char hex ID
    id: Mapped[str] = mapped_column(String(24), primary_key=True)

    # Board reference
    id_board: Mapped[str] = mapped_column(String(24), nullable=False, index=True)

    # Identity
    name: Mapped[str] = mapped_column(String(1000), nullable=False)

    # State
    closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    subscribed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Position
    pos: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Optional soft card limit
    soft_limit: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Rate-limit metadata
    limits: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
