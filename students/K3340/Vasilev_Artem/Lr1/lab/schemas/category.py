from pydantic import Field

from schemas.base import BaseSchema, TimestampedReadSchema


class CategoryCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=100, examples=["Study"])
    description: str | None = Field(default=None, max_length=1000, examples=["Tasks related to studying."])
    color: str | None = Field(default=None, max_length=20, examples=["#4F46E5"])


class CategoryUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    color: str | None = Field(default=None, max_length=20)


class CategoryRead(TimestampedReadSchema):
    id: int = Field(description="Category identifier.")
    name: str = Field(description="Category name.")
    description: str | None = Field(default=None, description="Category description.")
    color: str | None = Field(default=None, description="Visual color tag.")
    owner_id: int = Field(description="Category owner identifier.")
