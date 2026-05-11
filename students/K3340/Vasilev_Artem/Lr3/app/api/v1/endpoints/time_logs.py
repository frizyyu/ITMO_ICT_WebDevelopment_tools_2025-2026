from fastapi import APIRouter, Query, status

from core.dependencies import CurrentUser, DbSession
from schemas.time_log import TimeLogCreate, TimeLogRead, TimeLogUpdate
from services.time_log_service import TimeLogService

router = APIRouter(prefix="/time-logs", tags=["time-logs"])


@router.post("", response_model=TimeLogRead, status_code=status.HTTP_201_CREATED, summary="Create time log")
def create_time_log(
    payload: TimeLogCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> TimeLogRead:
    time_log = TimeLogService(session).create_time_log(payload, current_user)
    return TimeLogRead.model_validate(time_log)


@router.get("", response_model=list[TimeLogRead], summary="List current user time logs")
def list_time_logs(
    session: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of time logs to skip."),
    limit: int = Query(default=100, ge=1, le=100, description="Maximum number of time logs to return."),
) -> list[TimeLogRead]:
    logs = TimeLogService(session).list_time_logs(current_user, skip=skip, limit=limit)
    return [TimeLogRead.model_validate(log) for log in logs]


@router.get("/{log_id}", response_model=TimeLogRead, summary="Get time log by id")
def get_time_log(log_id: int, session: DbSession, current_user: CurrentUser) -> TimeLogRead:
    time_log = TimeLogService(session).get_time_log(log_id, current_user)
    return TimeLogRead.model_validate(time_log)


@router.put("/{log_id}", response_model=TimeLogRead, summary="Update time log")
def update_time_log(
    log_id: int,
    payload: TimeLogUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> TimeLogRead:
    time_log = TimeLogService(session).update_time_log(log_id, payload, current_user)
    return TimeLogRead.model_validate(time_log)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete time log")
def delete_time_log(log_id: int, session: DbSession, current_user: CurrentUser) -> None:
    TimeLogService(session).delete_time_log(log_id, current_user)
