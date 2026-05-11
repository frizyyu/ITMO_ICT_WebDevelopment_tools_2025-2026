from fastapi import APIRouter, Depends, status

from core.dependencies import CurrentUser, DbSession
from schemas.auth import ChangePasswordRequest, LoginRequest, RegisterRequest, TokenResponse
from schemas.user import UserRead
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(
    payload: RegisterRequest,
    session: DbSession,
) -> UserRead:
    service = AuthService(session)
    user = service.register_user(payload)
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and return access token",
)
def login_user(
    payload: LoginRequest,
    session: DbSession,
) -> TokenResponse:
    service = AuthService(session)
    return service.login(payload)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current authenticated user",
)
def get_me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change current user password",
)
def change_password(
    payload: ChangePasswordRequest,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    service = AuthService(session)
    service.change_password(current_user, payload)
