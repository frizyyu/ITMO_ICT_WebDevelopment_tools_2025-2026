from fastapi import APIRouter, Query, status

from core.dependencies import CurrentUser, DbSession
from schemas.notification import NotificationCreate, NotificationRead, NotificationUpdate
from services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post(
    "",
    response_model=NotificationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create notification",
)
def create_notification(
    payload: NotificationCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> NotificationRead:
    notification = NotificationService(session).create_notification(payload, current_user)
    return NotificationRead.model_validate(notification)


@router.get("", response_model=list[NotificationRead], summary="List current user notifications")
def list_notifications(
    session: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of notifications to skip."),
    limit: int = Query(default=100, ge=1, le=100, description="Maximum number of notifications to return."),
) -> list[NotificationRead]:
    notifications = NotificationService(session).list_notifications(current_user, skip=skip, limit=limit)
    return [NotificationRead.model_validate(item) for item in notifications]


@router.get("/{notification_id}", response_model=NotificationRead, summary="Get notification by id")
def get_notification(
    notification_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> NotificationRead:
    notification = NotificationService(session).get_notification(notification_id, current_user)
    return NotificationRead.model_validate(notification)


@router.put("/{notification_id}", response_model=NotificationRead, summary="Update notification")
def update_notification(
    notification_id: int,
    payload: NotificationUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> NotificationRead:
    notification = NotificationService(session).update_notification(notification_id, payload, current_user)
    return NotificationRead.model_validate(notification)


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification",
)
def delete_notification(
    notification_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    NotificationService(session).delete_notification(notification_id, current_user)
