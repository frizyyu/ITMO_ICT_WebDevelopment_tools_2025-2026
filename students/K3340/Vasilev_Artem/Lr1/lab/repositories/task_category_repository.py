from sqlalchemy import select
from sqlalchemy.orm import Session

from models.task_category import TaskCategory


class TaskCategoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_link(self, task_id: int, category_id: int) -> TaskCategory | None:
        statement = select(TaskCategory).where(
            TaskCategory.task_id == task_id,
            TaskCategory.category_id == category_id,
        )
        return self.session.scalar(statement)

    def create(self, link: TaskCategory) -> TaskCategory:
        self.session.add(link)
        self.session.flush()
        self.session.refresh(link)
        return link

    def delete(self, link: TaskCategory) -> None:
        self.session.delete(link)
        self.session.flush()
