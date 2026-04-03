from __future__ import annotations

from datetime import date

from pydantic import Field, model_validator

from models.enums import PlannedTaskStatus
from schemas.base import BaseSchema, TimestampedReadSchema
from schemas.task import TaskRead


class DailyPlanTaskCreate(BaseSchema):
    task_id: int = Field(description="Task identifier to include in the plan.")
    position: int = Field(default=0, ge=0, description="Display order inside the plan.")
    status: PlannedTaskStatus = Field(default=PlannedTaskStatus.PLANNED, description="Planned task state.")
    planned_minutes: int | None = Field(default=None, gt=0, description="Expected time allocation.")
    comment: str | None = Field(default=None, max_length=255, description="Short planning note.")


class DailyPlanTaskUpdate(BaseSchema):
    task_id: int | None = Field(default=None)
    position: int | None = Field(default=None, ge=0)
    status: PlannedTaskStatus | None = Field(default=None)
    planned_minutes: int | None = Field(default=None, gt=0)
    comment: str | None = Field(default=None, max_length=255)


class DailyPlanTaskRead(TimestampedReadSchema):
    id: int = Field(description="Planned task relation identifier.")
    daily_plan_id: int = Field(description="Daily plan identifier.")
    task_id: int = Field(description="Task identifier.")
    position: int = Field(description="Order in the daily plan.")
    status: PlannedTaskStatus = Field(description="Current state inside the plan.")
    planned_minutes: int | None = Field(default=None, description="Allocated time in minutes.")
    comment: str | None = Field(default=None, description="Optional note.")


class DailyPlanTaskReadWithTask(DailyPlanTaskRead):
    task: TaskRead = Field(description="Nested task details.")


class DailyPlanCreate(BaseSchema):
    plan_date: date = Field(description="Date of the daily plan.")
    notes: str | None = Field(default=None, max_length=2000, description="General notes for the day.")
    tasks: list[DailyPlanTaskCreate] = Field(default_factory=list, description="Tasks scheduled for the day.")


class DailyPlanUpdate(BaseSchema):
    plan_date: date | None = Field(default=None)
    notes: str | None = Field(default=None, max_length=2000)
    tasks: list[DailyPlanTaskUpdate] | None = Field(
        default=None,
        description="Optional full replacement payload for planned tasks.",
    )


class DailyPlanRead(TimestampedReadSchema):
    id: int = Field(description="Daily plan identifier.")
    user_id: int = Field(description="Owner identifier.")
    plan_date: date = Field(description="Date covered by the plan.")
    notes: str | None = Field(default=None, description="Plan notes.")


class DailyPlanReadWithTasks(DailyPlanRead):
    tasks: list[DailyPlanTaskReadWithTask] = Field(
        default_factory=list,
        description="Planned tasks with nested task objects.",
    )

    @model_validator(mode="before")
    @classmethod
    def populate_tasks(cls, value):
        if hasattr(value, "planned_tasks"):
            return {
                "id": value.id,
                "user_id": value.user_id,
                "plan_date": value.plan_date,
                "notes": value.notes,
                "created_at": value.created_at,
                "updated_at": value.updated_at,
                "tasks": list(value.planned_tasks),
            }
        return value
