from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, Enum):
    planned = "planned"
    in_progress = "in_progress"
    done = "done"
    overdue = "overdue"


class Category(BaseModel):
    id: int
    name: str
    color: str = Field(..., description="HEX color")


class TimeLog(BaseModel):
    id: int
    duration_minutes: int = Field(..., gt=0)
    note: str


class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    due_at: datetime
    category: Category
    time_logs: List[TimeLog] = []


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    due_at: datetime
    category: Category
    time_logs: List[TimeLog] = []


class CategoryCreate(BaseModel):
    name: str
    color: str = Field(..., description="HEX color")