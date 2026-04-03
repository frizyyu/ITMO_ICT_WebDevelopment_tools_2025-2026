from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from connection import get_session, init_db
from models import (
    Category,
    CategoryCreate,
    Tag,
    TagCreate,
    TagReadWithNote,
    Task,
    TaskCreate,
    TaskRead,
    TaskReadWithCategory,
    TaskReadWithDetails,
    TaskTagLink,
    TaskUpdate,
)

app = FastAPI(
    title="Task 2 - FastAPI Time Manager with SQLModel",
    description="Practice 1.2: FastAPI + PostgreSQL + SQLModel + relations.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {"message": "Hello! This is task2: SQLModel + PostgreSQL practice."}


# --------------------
# Categories
# --------------------
@app.get("/categories", response_model=List[Category], tags=["Categories"])
def get_categories(session: Session = Depends(get_session)) -> List[Category]:
    return session.exec(select(Category)).all()


@app.get("/categories/{category_id}", response_model=Category, tags=["Categories"])
def get_category(category_id: int, session: Session = Depends(get_session)) -> Category:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.post(
    "/categories",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    tags=["Categories"],
)
def create_category(category_data: CategoryCreate, session: Session = Depends(get_session)) -> Category:
    category = Category.model_validate(category_data)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


# --------------------
# Tags
# --------------------
@app.get("/tags", response_model=List[Tag], tags=["Tags"])
def get_tags(session: Session = Depends(get_session)) -> List[Tag]:
    return session.exec(select(Tag)).all()


@app.get("/tags/{tag_id}", response_model=Tag, tags=["Tags"])
def get_tag(tag_id: int, session: Session = Depends(get_session)) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.post("/tags", response_model=Tag, status_code=status.HTTP_201_CREATED, tags=["Tags"])
def create_tag(tag_data: TagCreate, session: Session = Depends(get_session)) -> Tag:
    tag = Tag.model_validate(tag_data)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


# --------------------
# Tasks
# --------------------
@app.get("/tasks", response_model=List[TaskRead], tags=["Tasks"])
def get_tasks(session: Session = Depends(get_session)) -> List[Task]:
    return session.exec(select(Task)).all()


@app.get("/tasks/{task_id}", response_model=TaskReadWithCategory, tags=["Tasks"])
def get_task(task_id: int, session: Session = Depends(get_session)) -> Task:
    statement = select(Task).where(Task.id == task_id).options(selectinload(Task.category))
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/tasks/{task_id}/details", response_model=TaskReadWithDetails, tags=["Tasks"])
def get_task_with_details(task_id: int, session: Session = Depends(get_session)) -> TaskReadWithDetails:
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
        TagReadWithNote(id=link.tag.id, name=link.tag.name, note=link.note)
        for link in task.tag_links
        if link.tag is not None
    ]

    return TaskReadWithDetails(
        id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        due_at=task.due_at,
        category_id=task.category_id,
        category=task.category,
        tags=tags,
    )


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


@app.patch("/tasks/{task_id}", response_model=TaskRead, tags=["Tasks"])
def update_task(task_id: int, task_data: TaskUpdate, session: Session = Depends(get_session)) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)

    if "category_id" in update_data and update_data["category_id"] is not None:
        category = session.get(Category, update_data["category_id"])
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}", tags=["Tasks"])
def delete_task(task_id: int, session: Session = Depends(get_session)) -> dict[str, bool]:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    links = session.exec(select(TaskTagLink).where(TaskTagLink.task_id == task_id)).all()
    for link in links:
        session.delete(link)

    session.delete(task)
    session.commit()
    return {"ok": True}


# --------------------
# Many-to-many: task <-> tag
# --------------------
@app.post("/tasks/{task_id}/tags/{tag_id}", response_model=TaskReadWithDetails, tags=["Tasks"])
def add_tag_to_task(
    task_id: int,
    tag_id: int,
    note: str = "main tag",
    session: Session = Depends(get_session),
) -> TaskReadWithDetails:
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

    link = TaskTagLink(task_id=task_id, tag_id=tag_id, note=note)
    session.add(link)
    session.commit()

    return get_task_with_details(task_id, session)