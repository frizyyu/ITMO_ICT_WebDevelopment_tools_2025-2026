from __future__ import annotations

import argparse
import asyncio
import socket
import time

import aiohttp

from common_parse import DEFAULT_URLS, HTTP_HEADERS, REQUEST_TIMEOUT_SECONDS, ParseResult, chunk_urls
from common_parse import page_title, parse_project_items, print_parse_result, save_projects, summarize_results

METHOD = "asyncio"


async def parse_and_save(url: str) -> ParseResult:
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
    connector = aiohttp.TCPConnector(family=socket.AF_INET)
    try:
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=HTTP_HEADERS,
            trust_env=True,
        ) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
        title = page_title(html)
        projects = parse_project_items(url, html)
        saved_count = await asyncio.to_thread(save_projects, projects, METHOD)
        result = ParseResult(
            url=url,
            title=title,
            parsed_by=METHOD,
            status="ok",
            extracted_count=len(projects),
            saved_count=saved_count,
        )
    except Exception as exc:
        error_message = repr(exc)
        print(f"[{METHOD}] Parse/save error for {url}: {error_message}", flush=True)
        result = ParseResult(url=url, title=None, parsed_by=METHOD, status="error", error=error_message)

    print_parse_result(result)
    return result


async def _process_chunk(urls: list[str]) -> list[ParseResult]:
    return await asyncio.gather(*(parse_and_save(url) for url in urls))


async def run_benchmark_async(urls: list[str] | None = None, workers: int = 4) -> dict[str, object]:
    target_urls = urls or DEFAULT_URLS
    url_chunks = chunk_urls(target_urls, workers)

    started_at = time.perf_counter()
    chunk_results = await asyncio.gather(*(_process_chunk(url_chunk) for url_chunk in url_chunks))
    elapsed = time.perf_counter() - started_at

    results = [result for chunk in chunk_results for result in chunk]
    return summarize_results(METHOD, started_at, elapsed, results)


def run_benchmark(urls: list[str] | None = None, workers: int = 4) -> dict[str, object]:
    return asyncio.run(run_benchmark_async(urls=urls, workers=workers))


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse web pages concurrently using asyncio and aiohttp.")
    parser.add_argument("--workers", type=int, default=4, help="Number of URL chunks.")
    parser.add_argument("--url", action="append", dest="urls", help="URL to parse. Can be passed multiple times.")
    args = parser.parse_args()

    result = run_benchmark(urls=args.urls, workers=args.workers)
    print(f"{METHOD}: saved={result['saved']} errors={result['errors']} elapsed={result['elapsed_seconds']:.6f}s", flush=True)


if __name__ == "__main__":
    main()
