from sqlalchemy import select
from sqlalchemy.orm import Session

from models.notification import Notification


class NotificationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, notification: Notification) -> Notification:
        self.session.add(notification)
        self.session.flush()
        self.session.refresh(notification)
        return notification

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Notification]:
        statement = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def get_by_id_and_user(self, notification_id: int, user_id: int) -> Notification | None:
        statement = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        return self.session.scalar(statement)

    def save(self, notification: Notification) -> Notification:
        self.session.add(notification)
        self.session.flush()
        self.session.refresh(notification)
        return notification

    def delete(self, notification: Notification) -> None:
        self.session.delete(notification)
        self.session.flush()
