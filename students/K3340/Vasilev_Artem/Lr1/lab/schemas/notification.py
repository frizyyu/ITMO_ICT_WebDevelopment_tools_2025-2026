from datetime import datetime

from pydantic import Field

from models.enums import NotificationType
from schemas.base import BaseSchema, TimestampedReadSchema


class NotificationCreate(BaseSchema):
    task_id: int | None = Field(default=None, description="Related task identifier if notification is task-bound.")
    type: NotificationType = Field(description="Notification type.")
    title: str = Field(min_length=1, max_length=255, examples=["Task reminder"])
    message: str = Field(min_length=1, max_length=2000, examples=["Do not forget to finish your report today."])
    scheduled_at: datetime | None = Field(default=None, description="When notification should be sent.")


class NotificationUpdate(BaseSchema):
    task_id: int | None = Field(default=None)
    type: NotificationType | None = Field(default=None)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    message: str | None = Field(default=None, min_length=1, max_length=2000)
    scheduled_at: datetime | None = Field(default=None)
    sent_at: datetime | None = Field(default=None)
    is_read: bool | None = Field(default=None)


class NotificationRead(TimestampedReadSchema):
    id: int = Field(description="Notification identifier.")
    user_id: int = Field(description="Recipient identifier.")
    task_id: int | None = Field(default=None, description="Related task identifier.")
    type: NotificationType = Field(description="Notification category.")
    title: str = Field(description="Notification title.")
    message: str = Field(description="Notification body.")
    scheduled_at: datetime | None = Field(default=None, description="Scheduled delivery time.")
    sent_at: datetime | None = Field(default=None, description="Actual send time.")
    is_read: bool = Field(description="Whether the user has read the notification.")
