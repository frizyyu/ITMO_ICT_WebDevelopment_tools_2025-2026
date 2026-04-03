from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password, verify_password
from models.user import User
from repositories.user_repository import UserRepository
from schemas.auth import ChangePasswordRequest, LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    def register_user(self, payload: RegisterRequest) -> User:
        existing_by_email = self.user_repository.get_by_email(payload.email)
        if existing_by_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists.",
            )

        existing_by_username = self.user_repository.get_by_username(payload.username)
        if existing_by_username is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists.",
            )

        user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            bio=payload.bio,
            is_active=True,
        )
        self.user_repository.create(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate_user(self, payload: LoginRequest) -> User:
        user = self.user_repository.get_by_login(payload.login)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.authenticate_user(payload)
        access_token = create_access_token(subject=user.id)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user,
        )

    def change_password(self, current_user: User, payload: ChangePasswordRequest) -> None:
        if not verify_password(payload.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        current_user.hashed_password = hash_password(payload.new_password)
        self.user_repository.save(current_user)
        self.session.commit()
