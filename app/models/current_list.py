from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CurrentList(Base):
    """Stores which Trello list IDs are designated as 'current' (today's task lists)."""

    __tablename__ = "current_lists"
    __table_args__ = (UniqueConstraint("list_id", name="uq_current_lists_list_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    list_id: Mapped[str] = mapped_column(String(24), nullable=False)
