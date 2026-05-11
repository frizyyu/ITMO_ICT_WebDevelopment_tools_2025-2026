from pydantic import EmailStr, Field

from schemas.base import BaseSchema, TimestampedReadSchema


class UserCreate(BaseSchema):
    username: str = Field(min_length=3, max_length=50, examples=["student01"])
    email: EmailStr = Field(examples=["student@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["StrongPass123"])
    full_name: str | None = Field(default=None, max_length=255, examples=["Ivan Petrov"])
    bio: str | None = Field(default=None, max_length=1000, examples=["Student of software engineering."])


class UserUpdate(BaseSchema):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=1000)
    is_active: bool | None = Field(default=None)


class UserRead(TimestampedReadSchema):
    id: int = Field(description="User identifier.")
    username: str = Field(description="Unique username.")
    email: EmailStr = Field(description="Unique email address.")
    full_name: str | None = Field(default=None, description="Public full name.")
    bio: str | None = Field(default=None, description="Short profile description.")
    is_active: bool = Field(description="Whether the account is active.")
