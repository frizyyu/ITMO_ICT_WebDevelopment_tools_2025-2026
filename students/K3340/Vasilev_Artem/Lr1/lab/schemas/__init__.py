"""Pydantic schemas package."""

from schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenPayload,
    TokenResponse,
)
from schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from schemas.daily_plan import (
    DailyPlanCreate,
    DailyPlanRead,
    DailyPlanReadWithTasks,
    DailyPlanTaskCreate,
    DailyPlanTaskRead,
    DailyPlanTaskReadWithTask,
    DailyPlanTaskUpdate,
    DailyPlanUpdate,
)
from schemas.notification import NotificationCreate, NotificationRead, NotificationUpdate
from schemas.task import TaskCreate, TaskRead, TaskReadWithDetails, TaskUpdate
from schemas.time_log import TimeLogCreate, TimeLogRead, TimeLogUpdate
from schemas.user import UserCreate, UserRead, UserUpdate

__all__ = [
    "LoginRequest",
    "RegisterRequest",
    "ChangePasswordRequest",
    "TokenPayload",
    "TokenResponse",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "TaskCreate",
    "TaskUpdate",
    "TaskRead",
    "TaskReadWithDetails",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryRead",
    "TimeLogCreate",
    "TimeLogUpdate",
    "TimeLogRead",
    "DailyPlanTaskCreate",
    "DailyPlanTaskUpdate",
    "DailyPlanTaskRead",
    "DailyPlanTaskReadWithTask",
    "DailyPlanCreate",
    "DailyPlanUpdate",
    "DailyPlanRead",
    "DailyPlanReadWithTasks",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationRead",
]
