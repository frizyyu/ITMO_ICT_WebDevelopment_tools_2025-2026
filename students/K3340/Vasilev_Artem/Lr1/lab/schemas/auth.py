from pydantic import Field

from schemas.base import BaseSchema
from schemas.user import UserCreate, UserRead


class LoginRequest(BaseSchema):
    login: str = Field(
        min_length=3,
        max_length=255,
        description="Username or email.",
        examples=["student@example.com"],
    )
    password: str = Field(min_length=8, max_length=128, examples=["StrongPass123"])


class RegisterRequest(UserCreate):
    pass


class ChangePasswordRequest(BaseSchema):
    current_password: str = Field(min_length=8, max_length=128, examples=["OldPass123"])
    new_password: str = Field(min_length=8, max_length=128, examples=["NewStrongPass123"])


class TokenResponse(BaseSchema):
    access_token: str = Field(description="JWT access token.")
    token_type: str = Field(default="bearer", description="Token scheme.")
    user: UserRead = Field(description="Authenticated user profile.")


class TokenPayload(BaseSchema):
    sub: str = Field(description="Subject identifier stored in JWT.")
