from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.task import Task
from models.task_category import TaskCategory
from models.user import User
from repositories.category_repository import CategoryRepository
from repositories.task_category_repository import TaskCategoryRepository
from repositories.task_repository import TaskRepository
from schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.task_repository = TaskRepository(session)
        self.category_repository = CategoryRepository(session)
        self.task_category_repository = TaskCategoryRepository(session)

    def create_task(self, payload: TaskCreate, current_user: User) -> Task:
        task = Task(owner_id=current_user.id, **payload.model_dump())
        self.task_repository.create(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def list_tasks(self, current_user: User, skip: int = 0, limit: int = 100) -> list[Task]:
        return self.task_repository.list_by_owner(current_user.id, skip=skip, limit=limit)

    def get_task(self, task_id: int, current_user: User) -> Task:
        task = self.task_repository.get_by_id_and_owner(task_id, current_user.id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
        return task

    def get_task_with_details(self, task_id: int, current_user: User) -> Task:
        task = self.task_repository.get_with_details(task_id, current_user.id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
        return task

    def update_task(self, task_id: int, payload: TaskUpdate, current_user: User) -> Task:
        task = self.get_task(task_id, current_user)
        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field_name, field_value)
        self.task_repository.save(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete_task(self, task_id: int, current_user: User) -> None:
        task = self.get_task(task_id, current_user)
        self.task_repository.delete(task)
        self.session.commit()

    def add_category(self, task_id: int, category_id: int, current_user: User) -> Task:
        task = self.get_task(task_id, current_user)
        category = self.category_repository.get_by_id_and_owner(category_id, current_user.id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

        existing_link = self.task_category_repository.get_link(task.id, category.id)
        if existing_link is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category is already attached to this task.",
            )

        self.task_category_repository.create(TaskCategory(task_id=task.id, category_id=category.id))
        self.session.commit()
        task_with_details = self.task_repository.get_with_details(task.id, current_user.id)
        if task_with_details is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
        return task_with_details

    def remove_category(self, task_id: int, category_id: int, current_user: User) -> None:
        self.get_task(task_id, current_user)
        category = self.category_repository.get_by_id_and_owner(category_id, current_user.id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

        link = self.task_category_repository.get_link(task_id, category_id)
        if link is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category link not found for this task.",
            )

        self.task_category_repository.delete(link)
        self.session.commit()
