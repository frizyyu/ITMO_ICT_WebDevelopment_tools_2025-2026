from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, status

from models import (
    Category,
    CategoryCreate,
    Task,
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TimeLog,
)

app = FastAPI(
    title="Task 1",
    description="Practice 1.1",
    version="1.0.0",
)

# In-memory "database" for categories
categories_db: List[Category] = [
    Category(id=1, name="Study", color="#FFAA00"),
    Category(id=2, name="Work", color="#4CAF50"),
    Category(id=3, name="Personal", color="#2196F3"),
]

# In-memory "database" for tasks
tasks_db: List[Task] = [
    Task(
        id=1,
        title="Prepare database lab",
        description="Read the materials and prepare the first draft.",
        priority=TaskPriority.high,
        status=TaskStatus.in_progress,
        due_at=datetime.fromisoformat("2026-04-05T18:00:00"),
        category=categories_db[0],
        time_logs=[
            TimeLog(id=1, duration_minutes=45, note="Read practice materials"),
            TimeLog(id=2, duration_minutes=30, note="Prepared draft outline"),
        ],
    ),
    Task(
        id=2,
        title="Write API report",
        description="Prepare the markdown report for the lab work.",
        priority=TaskPriority.medium,
        status=TaskStatus.planned,
        due_at=datetime.fromisoformat("2026-04-06T20:00:00"),
        category=categories_db[1],
        time_logs=[
            TimeLog(id=3, duration_minutes=25, note="Collected screenshots"),
        ],
    ),
    Task(
        id=3,
        title="Plan tomorrow",
        description="Create a short plan for the next study day.",
        priority=TaskPriority.low,
        status=TaskStatus.done,
        due_at=datetime.fromisoformat("2026-04-04T09:00:00"),
        category=categories_db[2],
        time_logs=[],
    ),
]


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {"message": "Hello! This is task1: basic FastAPI time manager."}


@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
def get_tasks() -> List[Task]:
    return tasks_db


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def get_task(task_id: int) -> Task:
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found",
    )


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(task_data: TaskCreate) -> Task:
    new_task_id = max((task.id for task in tasks_db), default=0) + 1
    new_task = Task(id=new_task_id, **task_data.model_dump())
    tasks_db.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def update_task(task_id: int, task_data: TaskCreate) -> Task:
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            updated_task = Task(id=task_id, **task_data.model_dump())
            tasks_db[index] = updated_task
            return updated_task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found",
    )


@app.delete("/tasks/{task_id}", tags=["Tasks"])
def delete_task(task_id: int) -> dict[str, str]:
    for index, task in enumerate(tasks_db):
        if task.id == task_id:
            tasks_db.pop(index)
            return {"message": "Task deleted"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found",
    )


@app.get("/categories", response_model=List[Category], tags=["Categories"])
def get_categories() -> List[Category]:
    return categories_db


@app.get("/categories/{category_id}", response_model=Category, tags=["Categories"])
def get_category(category_id: int) -> Category:
    for category in categories_db:
        if category.id == category_id:
            return category
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Category not found",
    )


@app.post(
    "/categories",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    tags=["Categories"],
)
def create_category(category_data: CategoryCreate) -> Category:
    new_category_id = max((category.id for category in categories_db), default=0) + 1
    new_category = Category(id=new_category_id, **category_data.model_dump())
    categories_db.append(new_category)
    return new_category