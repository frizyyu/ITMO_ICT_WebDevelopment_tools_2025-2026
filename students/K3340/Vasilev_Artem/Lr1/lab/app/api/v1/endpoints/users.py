from fastapi import APIRouter, Query

from core.dependencies import CurrentUser, DbSession
from schemas.user import UserRead
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=list[UserRead],
    summary="List users",
)
def list_users(
    session: DbSession,
    _: CurrentUser,
    skip: int = Query(default=0, ge=0, description="Number of users to skip."),
    limit: int = Query(default=100, ge=1, le=100, description="Maximum number of users to return."),
) -> list[UserRead]:
    service = UserService(session)
    users = service.list_users(skip=skip, limit=limit)
    return [UserRead.model_validate(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user by id",
)
def get_user_by_id(
    user_id: int,
    session: DbSession,
    _: CurrentUser,
) -> UserRead:
    service = UserService(session)
    user = service.get_user_by_id(user_id)
    return UserRead.model_validate(user)
