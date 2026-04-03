import math
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.time_log import TimeLog
from models.user import User
from repositories.task_repository import TaskRepository
from repositories.time_log_repository import TimeLogRepository
from schemas.time_log import TimeLogCreate, TimeLogUpdate


class TimeLogService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.time_log_repository = TimeLogRepository(session)
        self.task_repository = TaskRepository(session)

    def _get_owned_task(self, task_id: int, current_user: User):
        task = self.task_repository.get_by_id_and_owner(task_id, current_user.id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
        return task

    @staticmethod
    def _calculate_duration_minutes(started_at, ended_at) -> int | None:
        if ended_at is None:
            return None
        delta: timedelta = ended_at - started_at
        minutes = math.ceil(delta.total_seconds() / 60)
        return minutes if minutes > 0 else None

    @staticmethod
    def _validate_time_range(started_at, ended_at) -> None:
        if ended_at is not None and ended_at <= started_at:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="ended_at must be greater than started_at.",
            )

    def create_time_log(self, payload: TimeLogCreate, current_user: User) -> TimeLog:
        self._get_owned_task(payload.task_id, current_user)
        self._validate_time_range(payload.started_at, payload.ended_at)
        duration_minutes = payload.duration_minutes
        if duration_minutes is None and payload.ended_at is not None:
            duration_minutes = self._calculate_duration_minutes(payload.started_at, payload.ended_at)

        time_log = TimeLog(
            user_id=current_user.id,
            task_id=payload.task_id,
            started_at=payload.started_at,
            ended_at=payload.ended_at,
            duration_minutes=duration_minutes,
            note=payload.note,
        )
        self.time_log_repository.create(time_log)
        self.session.commit()
        self.session.refresh(time_log)
        return time_log

    def list_time_logs(self, current_user: User, skip: int = 0, limit: int = 100) -> list[TimeLog]:
        return self.time_log_repository.list_by_user(current_user.id, skip=skip, limit=limit)

    def get_time_log(self, log_id: int, current_user: User) -> TimeLog:
        time_log = self.time_log_repository.get_by_id_and_user(log_id, current_user.id)
        if time_log is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time log not found.")
        return time_log

    def update_time_log(self, log_id: int, payload: TimeLogUpdate, current_user: User) -> TimeLog:
        time_log = self.get_time_log(log_id, current_user)
        data = payload.model_dump(exclude_unset=True)
        started_at = data.get("started_at", time_log.started_at)
        ended_at = data.get("ended_at", time_log.ended_at)
        self._validate_time_range(started_at, ended_at)
        if "duration_minutes" not in data:
            data["duration_minutes"] = self._calculate_duration_minutes(started_at, ended_at)

        for field_name, field_value in data.items():
            setattr(time_log, field_name, field_value)

        self.time_log_repository.save(time_log)
        self.session.commit()
        self.session.refresh(time_log)
        return time_log

    def delete_time_log(self, log_id: int, current_user: User) -> None:
        time_log = self.get_time_log(log_id, current_user)
        self.time_log_repository.delete(time_log)
        self.session.commit()
