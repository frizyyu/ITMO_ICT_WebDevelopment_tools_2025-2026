from datetime import datetime

from pydantic import Field, model_validator

from schemas.base import BaseSchema, TimestampedReadSchema


class TimeLogCreate(BaseSchema):
    task_id: int = Field(description="Task identifier.")
    started_at: datetime = Field(description="Start timestamp of the work session.")
    ended_at: datetime | None = Field(default=None, description="Finish timestamp of the work session.")
    duration_minutes: int | None = Field(default=None, gt=0, examples=[45])
    note: str | None = Field(default=None, max_length=1000, examples=["Worked on the report."])

    @model_validator(mode="after")
    def validate_time_range(self) -> "TimeLogCreate":
        if self.ended_at is not None and self.ended_at <= self.started_at:
            raise ValueError("ended_at must be greater than started_at")
        return self


class TimeLogUpdate(BaseSchema):
    started_at: datetime | None = Field(default=None)
    ended_at: datetime | None = Field(default=None)
    duration_minutes: int | None = Field(default=None, gt=0)
    note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_time_range(self) -> "TimeLogUpdate":
        if (
            self.started_at is not None
            and self.ended_at is not None
            and self.ended_at <= self.started_at
        ):
            raise ValueError("ended_at must be greater than started_at")
        return self


class TimeLogRead(TimestampedReadSchema):
    id: int = Field(description="Time log identifier.")
    user_id: int = Field(description="Owner identifier.")
    task_id: int = Field(description="Related task identifier.")
    started_at: datetime = Field(description="Start timestamp.")
    ended_at: datetime | None = Field(default=None, description="Finish timestamp.")
    duration_minutes: int | None = Field(default=None, description="Duration in minutes.")
    note: str | None = Field(default=None, description="Optional comment.")
