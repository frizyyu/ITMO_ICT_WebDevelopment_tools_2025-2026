from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from models.task import Task
from models.task_category import TaskCategory


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, task: Task) -> Task:
        self.session.add(task)
        self.session.flush()
        self.session.refresh(task)
        return task

    def list_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> list[Task]:
        statement = (
            select(Task)
            .where(Task.owner_id == owner_id)
            .order_by(Task.id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def get_by_id(self, task_id: int) -> Task | None:
        statement = select(Task).where(Task.id == task_id)
        return self.session.scalar(statement)

    def get_by_id_and_owner(self, task_id: int, owner_id: int) -> Task | None:
        statement = select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        return self.session.scalar(statement)

    def get_with_details(self, task_id: int, owner_id: int) -> Task | None:
        statement: Select[tuple[Task]] = (
            select(Task)
            .where(Task.id == task_id, Task.owner_id == owner_id)
            .options(
                selectinload(Task.owner),
                selectinload(Task.time_logs),
                selectinload(Task.category_links).selectinload(TaskCategory.category),
            )
        )
        return self.session.scalar(statement)

    def save(self, task: Task) -> Task:
        self.session.add(task)
        self.session.flush()
        self.session.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.session.delete(task)
        self.session.flush()
