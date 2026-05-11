from fastapi import APIRouter, Query, status

from core.dependencies import CurrentUser, DbSession
from schemas.daily_plan import DailyPlanCreate, DailyPlanRead, DailyPlanReadWithTasks, DailyPlanUpdate
from services.daily_plan_service import DailyPlanService

router = APIRouter(prefix="/daily-plans", tags=["daily-plans"])


@router.post(
    "",
    response_model=DailyPlanReadWithTasks,
    status_code=status.HTTP_201_CREATED,
    summary="Create daily plan",
)
def create_daily_plan(
    payload: DailyPlanCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> DailyPlanReadWithTasks:
    plan = DailyPlanService(session).create_daily_plan(payload, current_user)
    return DailyPlanReadWithTasks.model_validate(plan)


@router.get("", response_model=list[DailyPlanRead], summary="List current user daily plans")
def list_daily_plans(
    session: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of daily plans to skip."),
    limit: int = Query(default=100, ge=1, le=100, description="Maximum number of daily plans to return."),
) -> list[DailyPlanRead]:
    plans = DailyPlanService(session).list_daily_plans(current_user, skip=skip, limit=limit)
    return [DailyPlanRead.model_validate(plan) for plan in plans]


@router.get("/{plan_id}", response_model=DailyPlanRead, summary="Get daily plan by id")
def get_daily_plan(plan_id: int, session: DbSession, current_user: CurrentUser) -> DailyPlanRead:
    plan = DailyPlanService(session).get_daily_plan(plan_id, current_user)
    return DailyPlanRead.model_validate(plan)


@router.put("/{plan_id}", response_model=DailyPlanReadWithTasks, summary="Update daily plan")
def update_daily_plan(
    plan_id: int,
    payload: DailyPlanUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> DailyPlanReadWithTasks:
    plan = DailyPlanService(session).update_daily_plan(plan_id, payload, current_user)
    return DailyPlanReadWithTasks.model_validate(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete daily plan")
def delete_daily_plan(plan_id: int, session: DbSession, current_user: CurrentUser) -> None:
    DailyPlanService(session).delete_daily_plan(plan_id, current_user)


@router.get(
    "/{plan_id}/with-tasks",
    response_model=DailyPlanReadWithTasks,
    summary="Get daily plan with planned tasks",
)
def get_daily_plan_with_tasks(
    plan_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> DailyPlanReadWithTasks:
    plan = DailyPlanService(session).get_daily_plan_with_tasks(plan_id, current_user)
    return DailyPlanReadWithTasks.model_validate(plan)


@router.post(
    "/{plan_id}/tasks/{task_id}",
    response_model=DailyPlanReadWithTasks,
    summary="Attach task to daily plan",
)
def add_task_to_daily_plan(
    plan_id: int,
    task_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> DailyPlanReadWithTasks:
    plan = DailyPlanService(session).add_task_to_plan(plan_id, task_id, current_user)
    return DailyPlanReadWithTasks.model_validate(plan)


@router.delete(
    "/{plan_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Detach task from daily plan",
)
def remove_task_from_daily_plan(
    plan_id: int,
    task_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    DailyPlanService(session).remove_task_from_plan(plan_id, task_id, current_user)
