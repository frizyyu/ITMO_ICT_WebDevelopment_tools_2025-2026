from enum import StrEnum


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class PlannedTaskStatus(StrEnum):
    PLANNED = "planned"
    DONE = "done"
    SKIPPED = "skipped"
    MOVED = "moved"


class NotificationType(StrEnum):
    REMINDER = "reminder"
    DEADLINE = "deadline"
    SYSTEM = "system"
    DAILY_PLAN = "daily_plan"
