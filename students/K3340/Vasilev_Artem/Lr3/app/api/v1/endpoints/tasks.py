from fastapi import APIRouter, Query, status

from core.dependencies import CurrentUser, DbSession
from schemas.task import TaskCreate, TaskRead, TaskReadWithDetails, TaskUpdate
from services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED, summary="Create task")
def create_task(payload: TaskCreate, session: DbSession, current_user: CurrentUser) -> TaskRead:
    task = TaskService(session).create_task(payload, current_user)
    return TaskRead.model_validate(task)


@router.get("", response_model=list[TaskRead], summary="List current user tasks")
def list_tasks(
    session: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of tasks to skip."),
    limit: int = Query(default=100, ge=1, le=100, description="Maximum number of tasks to return."),
) -> list[TaskRead]:
    tasks = TaskService(session).list_tasks(current_user, skip=skip, limit=limit)
    return [TaskRead.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskRead, summary="Get task by id")
def get_task(task_id: int, session: DbSession, current_user: CurrentUser) -> TaskRead:
    task = TaskService(session).get_task(task_id, current_user)
    return TaskRead.model_validate(task)


@router.put("/{task_id}", response_model=TaskRead, summary="Update task")
def update_task(
    task_id: int,
    payload: TaskUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> TaskRead:
    task = TaskService(session).update_task(task_id, payload, current_user)
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete task")
def delete_task(task_id: int, session: DbSession, current_user: CurrentUser) -> None:
    TaskService(session).delete_task(task_id, current_user)


@router.get(
    "/{task_id}/with-details",
    response_model=TaskReadWithDetails,
    summary="Get task with owner, categories and time logs",
)
def get_task_with_details(
    task_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> TaskReadWithDetails:
    task = TaskService(session).get_task_with_details(task_id, current_user)
    return TaskReadWithDetails.model_validate(task)


@router.post(
    "/{task_id}/categories/{category_id}",
    response_model=TaskReadWithDetails,
    summary="Attach category to task",
)
def add_category_to_task(
    task_id: int,
    category_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> TaskReadWithDetails:
    task = TaskService(session).add_category(task_id, category_id, current_user)
    return TaskReadWithDetails.model_validate(task)


@router.delete(
    "/{task_id}/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Detach category from task",
)
def remove_category_from_task(
    task_id: int,
    category_id: int,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    TaskService(session).remove_category(task_id, category_id, current_user)
