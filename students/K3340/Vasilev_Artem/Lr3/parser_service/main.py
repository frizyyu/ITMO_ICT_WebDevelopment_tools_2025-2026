from fastapi import FastAPI

from parser.asyncio_parse import run_benchmark_async
from parser_service.schemas import ParseRequest, ParseResponse

app = FastAPI(
    title="LR3 Parser Service",
    description="HTTP wrapper around the LR2 asyncio parser.",
    version="0.1.0",
)


@app.get("/health", summary="Parser service health check")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "parser-service"}


@app.post("/parse", response_model=ParseResponse, summary="Parse URLs and save projects to database")
async def parse_urls(payload: ParseRequest) -> ParseResponse:
    result = await run_benchmark_async(urls=payload.urls, workers=payload.workers)
    return ParseResponse.model_validate(result)
