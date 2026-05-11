from pydantic import BaseModel, Field

from parser.common_parse import DEFAULT_URLS


class ParseRequest(BaseModel):
    urls: list[str] = Field(default_factory=lambda: list(DEFAULT_URLS), min_length=1)
    workers: int = Field(default=4, ge=1, le=16)


class ParseResponse(BaseModel):
    method: str
    started_at: float
    urls: int
    saved: int
    extracted: int
    ok: int
    errors: int
    elapsed_seconds: float
    items: list[dict[str, object]]
