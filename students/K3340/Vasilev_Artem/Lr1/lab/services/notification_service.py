from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.notification import Notification
from models.user import User
from repositories.notification_repository import NotificationRepository
from repositories.task_repository import TaskRepository
from schemas.notification import NotificationCreate, NotificationUpdate


class NotificationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.notification_repository = NotificationRepository(session)
        self.task_repository = TaskRepository(session)

    def _validate_task_ownership(self, task_id: int | None, current_user: User) -> None:
        if task_id is None:
            return
        task = self.task_repository.get_by_id_and_owner(task_id, current_user.id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    def create_notification(self, payload: NotificationCreate, current_user: User) -> Notification:
        self._validate_task_ownership(payload.task_id, current_user)
        notification = Notification(user_id=current_user.id, **payload.model_dump())
        self.notification_repository.create(notification)
        self.session.commit()
        self.session.refresh(notification)
        return notification

    def list_notifications(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Notification]:
        return self.notification_repository.list_by_user(current_user.id, skip=skip, limit=limit)

    def get_notification(self, notification_id: int, current_user: User) -> Notification:
        notification = self.notification_repository.get_by_id_and_user(notification_id, current_user.id)
        if notification is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
        return notification

    def update_notification(
        self,
        notification_id: int,
        payload: NotificationUpdate,
        current_user: User,
    ) -> Notification:
        notification = self.get_notification(notification_id, current_user)
        data = payload.model_dump(exclude_unset=True)
        if "task_id" in data:
            self._validate_task_ownership(data["task_id"], current_user)
        for field_name, field_value in data.items():
            setattr(notification, field_name, field_value)
        self.notification_repository.save(notification)
        self.session.commit()
        self.session.refresh(notification)
        return notification

    def delete_notification(self, notification_id: int, current_user: User) -> None:
        notification = self.get_notification(notification_id, current_user)
        self.notification_repository.delete(notification)
        self.session.commit()
