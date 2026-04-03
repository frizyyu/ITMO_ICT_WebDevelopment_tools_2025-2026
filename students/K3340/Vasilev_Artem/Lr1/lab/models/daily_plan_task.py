from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.enums import PlannedTaskStatus
from models.mixins import TimestampMixin

if TYPE_CHECKING:
    from models.daily_plan import DailyPlan
    from models.task import Task


class DailyPlanTask(TimestampMixin, Base):
    __tablename__ = "daily_plan_tasks"
    __table_args__ = (
        UniqueConstraint("daily_plan_id", "task_id", name="uq_daily_plan_tasks_daily_plan_id_task_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    daily_plan_id: Mapped[int] = mapped_column(
        ForeignKey("daily_plans.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[PlannedTaskStatus] = mapped_column(
        Enum(
            PlannedTaskStatus,
            name="planned_task_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=PlannedTaskStatus.PLANNED,
        nullable=False,
    )
    planned_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)

    daily_plan: Mapped["DailyPlan"] = relationship(back_populates="planned_tasks")
    task: Mapped["Task"] = relationship(back_populates="daily_plan_links")
