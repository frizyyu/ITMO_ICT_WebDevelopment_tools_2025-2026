from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.enums import TaskPriority, TaskStatus
from models.mixins import TimestampMixin

if TYPE_CHECKING:
    from models.daily_plan_task import DailyPlanTask
    from models.notification import Notification
    from models.task_category import TaskCategory
    from models.time_log import TimeLog
    from models.user import User


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(
            TaskPriority,
            name="task_priority",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            name="task_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=TaskStatus.PENDING,
        nullable=False,
    )
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    owner: Mapped["User"] = relationship(back_populates="tasks")
    category_links: Mapped[list["TaskCategory"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    time_logs: Mapped[list["TimeLog"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    daily_plan_links: Mapped[list["DailyPlanTask"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
