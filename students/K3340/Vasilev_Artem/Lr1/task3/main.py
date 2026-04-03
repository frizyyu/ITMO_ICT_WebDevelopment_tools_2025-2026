from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from connection import get_session
from models import (
    Category,
    CategoryCreate,
    Tag,
    TagCreate,
    TagRead,
    Task,
    TaskCreate,
    TaskRead,
    TaskTagLink,
)

app = FastAPI(
    title="Task 3 - FastAPI Time Manager with ENV and Alembic",
    description="Practice 1.3: FastAPI + SQLModel + PostgreSQL + .env + Alembic.",
    version="1.0.0",
)


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {"message": "Hello! This is task3: env + alembic + structure practice."}


@app.get("/categories", response_model=List[Category], tags=["Categories"])
def get_categories(session: Session = Depends(get_session)) -> List[Category]:
    return session.exec(select(Category)).all()


@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED, tags=["Categories"])
def create_category(category_data: CategoryCreate, session: Session = Depends(get_session)) -> Category:
    category = Category.model_validate(category_data)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@app.get("/tags", response_model=List[Tag], tags=["Tags"])
def get_tags(session: Session = Depends(get_session)) -> List[Tag]:
    return session.exec(select(Tag)).all()


@app.post("/tags", response_model=Tag, status_code=status.HTTP_201_CREATED, tags=["Tags"])
def create_tag(tag_data: TagCreate, session: Session = Depends(get_session)) -> Tag:
    tag = Tag.model_validate(tag_data)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@app.get("/tasks", response_model=List[TaskRead], tags=["Tasks"])
def get_tasks(session: Session = Depends(get_session)) -> List[Task]:
    return session.exec(select(Task)).all()


@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(task_data: TaskCreate, session: Session = Depends(get_session)) -> Task:
    if task_data.category_id is not None:
        category = session.get(Category, task_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    task = Task.model_validate(task_data)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.post("/tasks/{task_id}/tags/{tag_id}", tags=["Tasks"])
def add_tag_to_task(
    task_id: int,
    tag_id: int,
    note: str = Query(default="main tag"),
    importance_level: int = Query(default=1, ge=1, le=10),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    existing_link = session.exec(
        select(TaskTagLink).where(
            TaskTagLink.task_id == task_id,
            TaskTagLink.tag_id == tag_id,
        )
    ).first()

    if existing_link:
        raise HTTPException(status_code=400, detail="Tag already attached to task")

    link = TaskTagLink(
        task_id=task_id,
        tag_id=tag_id,
        note=note,
        importance_level=importance_level,
    )
    session.add(link)
    session.commit()

    return {"message": "Tag attached to task"}


@app.get("/tasks/{task_id}/details", tags=["Tasks"])
def get_task_details(task_id: int, session: Session = Depends(get_session)) -> dict:
    statement = (
        select(Task)
        .where(Task.id == task_id)
        .options(
            selectinload(Task.category),
            selectinload(Task.tag_links).selectinload(TaskTagLink.tag),
        )
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    tags = [
        TagRead(
            id=link.tag.id,
            name=link.tag.name,
            note=link.note,
            importance_level=link.importance_level,
        )
        for link in task.tag_links
        if link.tag is not None
    ]

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "due_at": task.due_at,
        "category_id": task.category_id,
        "category": task.category,
        "tags": tags,
    }