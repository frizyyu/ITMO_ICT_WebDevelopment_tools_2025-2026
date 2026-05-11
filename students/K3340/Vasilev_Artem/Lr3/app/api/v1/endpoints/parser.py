from urllib.parse import urljoin

import requests
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status

from core.dependencies import AppSettings
from schemas.parser import ParserRequest, ParserResponse, ParserTaskQueuedResponse, ParserTaskStatusResponse
from worker.celery_app import celery_app
from worker.tasks import parse_urls_task

router = APIRouter(prefix="/parser", tags=["parser"])


@router.post(
    "/parse-sync",
    response_model=ParserResponse,
    summary="Synchronously call parser-service",
)
def parse_sync(payload: ParserRequest, settings: AppSettings) -> ParserResponse:
    parser_url = urljoin(settings.parser_service_url.rstrip("/") + "/", "parse")

    try:
        response = requests.post(
            parser_url,
            json=payload.model_dump(),
            timeout=120,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Parser service is unavailable: {exc}",
        ) from exc

    if response.status_code >= 500:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "Parser service returned an error.",
                "status_code": response.status_code,
                "body": response.text,
            },
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": "Parser service rejected the request.",
                "body": response.text,
            },
        )

    try:
        return ParserResponse.model_validate(response.json())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Parser service returned invalid JSON.",
        ) from exc


@router.post(
    "/parse-async",
    response_model=ParserTaskQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue parser-service call in Celery",
)
def parse_async(payload: ParserRequest) -> ParserTaskQueuedResponse:
    task = parse_urls_task.delay(payload.urls, payload.workers)
    return ParserTaskQueuedResponse(task_id=task.id, status="queued")


@router.get(
    "/tasks/{task_id}",
    response_model=ParserTaskStatusResponse,
    summary="Get parser task status",
)
def get_parser_task_status(task_id: str) -> ParserTaskStatusResponse:
    task = AsyncResult(task_id, app=celery_app)

    if task.successful():
        return ParserTaskStatusResponse(
            task_id=task_id,
            status=task.status,
            result=task.result,
        )

    if task.failed():
        return ParserTaskStatusResponse(
            task_id=task_id,
            status=task.status,
            error=str(task.result),
        )

    return ParserTaskStatusResponse(task_id=task_id, status=task.status)
