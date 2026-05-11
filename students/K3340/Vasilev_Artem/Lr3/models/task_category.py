from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.mixins import TimestampMixin

if TYPE_CHECKING:
    from models.category import Category
    from models.task import Task


class TaskCategory(TimestampMixin, Base):
    __tablename__ = "task_categories"
    __table_args__ = (
        UniqueConstraint("task_id", "category_id", name="uq_task_categories_task_id_category_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)

    task: Mapped["Task"] = relationship(back_populates="category_links")
    category: Mapped["Category"] = relationship(back_populates="task_links")
