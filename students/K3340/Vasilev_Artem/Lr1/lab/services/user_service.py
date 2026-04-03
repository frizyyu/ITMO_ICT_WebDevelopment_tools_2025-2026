from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, session: Session) -> None:
        self.user_repository = UserRepository(session)

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.user_repository.list_users(skip=skip, limit=limit)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user
