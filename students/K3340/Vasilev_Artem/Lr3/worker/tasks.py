import os
from urllib.parse import urljoin

import requests

from parser.common_parse import DEFAULT_URLS
from worker.celery_app import celery_app


def call_parser_service(urls: list[str], workers: int) -> dict[str, object]:
    parser_service_url = os.getenv("PARSER_SERVICE_URL", "http://parser-service:8001")
    parser_url = urljoin(parser_service_url.rstrip("/") + "/", "parse")

    try:
        response = requests.post(
            parser_url,
            json={"urls": urls, "workers": workers},
            timeout=300,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Parser service request failed: {exc}") from exc

    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError("Parser service returned invalid JSON.") from exc

    if not isinstance(result, dict):
        raise RuntimeError("Parser service returned an unexpected response shape.")

    return result


@celery_app.task(name="worker.tasks.parse_urls_task")
def parse_urls_task(urls: list[str], workers: int = 4) -> dict[str, object]:
    return call_parser_service(urls=urls, workers=workers)


@celery_app.task(name="worker.tasks.parse_default_urls_task")
def parse_default_urls_task(workers: int = 4) -> dict[str, object]:
    return call_parser_service(urls=list(DEFAULT_URLS), workers=workers)
