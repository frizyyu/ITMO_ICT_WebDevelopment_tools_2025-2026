from __future__ import annotations

from datetime import datetime

from pydantic import Field, model_validator

from models.enums import TaskPriority, TaskStatus
from schemas.base import BaseSchema, ORMReadSchema, TimestampedReadSchema
from schemas.category import CategoryRead
from schemas.time_log import TimeLogRead
from schemas.user import UserRead


class TaskCreate(BaseSchema):
    title: str = Field(min_length=1, max_length=255, examples=["Prepare database lab"])
    description: str | None = Field(default=None, max_length=3000, examples=["Write models and migrations."])
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority.")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task workflow status.")
    estimated_minutes: int | None = Field(default=None, gt=0, examples=[90])
    due_at: datetime | None = Field(default=None, description="Planned deadline.")


class TaskUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=3000)
    priority: TaskPriority | None = Field(default=None)
    status: TaskStatus | None = Field(default=None)
    estimated_minutes: int | None = Field(default=None, gt=0)
    due_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)


class TaskRead(TimestampedReadSchema):
    id: int = Field(description="Task identifier.")
    title: str = Field(description="Task title.")
    description: str | None = Field(default=None, description="Task description.")
    priority: TaskPriority = Field(description="Task priority.")
    status: TaskStatus = Field(description="Task status.")
    estimated_minutes: int | None = Field(default=None, description="Estimated effort in minutes.")
    due_at: datetime | None = Field(default=None, description="Task deadline.")
    completed_at: datetime | None = Field(default=None, description="Task completion time.")
    owner_id: int = Field(description="Task owner identifier.")


class TaskCategoryLinkRead(ORMReadSchema):
    label: str | None = Field(default=None, description="Optional label on task-category relation.")
    category: CategoryRead = Field(description="Linked category.")


class TaskReadWithDetails(TaskRead):
    owner: UserRead = Field(description="Task owner.")
    categories: list[CategoryRead] = Field(default_factory=list, description="Categories assigned to the task.")
    time_logs: list[TimeLogRead] = Field(default_factory=list, description="Work sessions logged for the task.")

    @model_validator(mode="before")
    @classmethod
    def populate_categories(cls, value):
        if hasattr(value, "category_links"):
            data = {
                "id": value.id,
                "title": value.title,
                "description": value.description,
                "priority": value.priority,
                "status": value.status,
                "estimated_minutes": value.estimated_minutes,
                "due_at": value.due_at,
                "completed_at": value.completed_at,
                "owner_id": value.owner_id,
                "created_at": value.created_at,
                "updated_at": value.updated_at,
                "owner": value.owner,
                "categories": [
                    link.category
                    for link in value.category_links
                    if getattr(link, "category", None) is not None
                ],
                "time_logs": list(getattr(value, "time_logs", [])),
            }
            return data
        return value
