from pydantic import Field

from schemas.base import BaseSchema


class ParserRequest(BaseSchema):
    urls: list[str] = Field(min_length=1, description="URLs to parse.")
    workers: int = Field(default=4, ge=1, le=16, description="Number of parser workers.")


class ParserResponse(BaseSchema):
    method: str
    started_at: float
    urls: int
    saved: int
    extracted: int
    ok: int
    errors: int
    elapsed_seconds: float
    items: list[dict[str, object]]


class ParserTaskQueuedResponse(BaseSchema):
    task_id: str
    status: str


class ParserTaskStatusResponse(BaseSchema):
    task_id: str
    status: str
    result: dict[str, object] | None = None
    error: str | None = None
