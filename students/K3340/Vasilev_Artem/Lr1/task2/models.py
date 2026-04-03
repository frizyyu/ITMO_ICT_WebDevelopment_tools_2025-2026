from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, Enum):
    planned = "planned"
    in_progress = "in_progress"
    done = "done"
    overdue = "overdue"


class CategoryBase(SQLModel):
    name: str
    color: str


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tasks: List["Task"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    pass


class TagBase(SQLModel):
    name: str


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_links: List["TaskTagLink"] = Relationship(back_populates="tag")


class TagCreate(TagBase):
    pass


class TaskTagLinkBase(SQLModel):
    note: Optional[str] = None


class TaskTagLink(TaskTagLinkBase, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)

    task: Optional["Task"] = Relationship(back_populates="tag_links")
    tag: Optional["Tag"] = Relationship(back_populates="task_links")


class TaskBase(SQLModel):
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    due_at: datetime
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    category: Optional[Category] = Relationship(back_populates="tasks")
    tag_links: List[TaskTagLink] = Relationship(back_populates="task")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_at: Optional[datetime] = None
    category_id: Optional[int] = None


class TaskRead(TaskBase):
    id: int


class TaskReadWithCategory(TaskRead):
    category: Optional[Category] = None


class TagReadWithNote(SQLModel):
    id: int
    name: str
    note: Optional[str] = None


class TaskReadWithDetails(TaskRead):
    category: Optional[Category] = None
    tags: List[TagReadWithNote] = []