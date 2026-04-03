from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class ORMReadSchema(BaseSchema):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampedReadSchema(ORMReadSchema):
    created_at: datetime = Field(description="Entity creation timestamp.")
    updated_at: datetime = Field(description="Entity last update timestamp.")
