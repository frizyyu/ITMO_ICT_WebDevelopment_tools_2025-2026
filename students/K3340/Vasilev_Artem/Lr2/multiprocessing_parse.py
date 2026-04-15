from __future__ import annotations

import argparse
import multiprocessing
import time

import requests

from common_parse import DEFAULT_URLS, HTTP_HEADERS, REQUEST_TIMEOUT_SECONDS, ParseResult, chunk_urls
from common_parse import page_title, parse_project_items, print_parse_result, save_projects, summarize_results

METHOD = "multiprocessing"


def parse_and_save(url: str) -> ParseResult:
    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        title = page_title(response.text)
        projects = parse_project_items(url, response.text)
        saved_count = save_projects(projects, METHOD)
        result = ParseResult(
            url=url,
            title=title,
            parsed_by=METHOD,
            status="ok",
            extracted_count=len(projects),
            saved_count=saved_count,
        )
    except Exception as exc:
        print(f"[{METHOD}] Parse/save error for {url}: {exc}", flush=True)
        result = ParseResult(url=url, title=None, parsed_by=METHOD, status="error", error=str(exc))
    print_parse_result(result)
    return result


def _worker(urls: list[str], queue: multiprocessing.Queue) -> None:
    chunk_results = [parse_and_save(url) for url in urls]
    queue.put(chunk_results)


def run_benchmark(urls: list[str] | None = None, workers: int = 4) -> dict[str, object]:
    target_urls = urls or DEFAULT_URLS
    url_chunks = chunk_urls(target_urls, workers)
    queue: multiprocessing.Queue = multiprocessing.Queue()
    processes: list[multiprocessing.Process] = []

    started_at = time.perf_counter()
    for url_chunk in url_chunks:
        process = multiprocessing.Process(target=_worker, args=(url_chunk, queue))
        processes.append(process)
        process.start()

    results: list[ParseResult] = []
    for _ in processes:
        results.extend(queue.get())

    for process in processes:
        process.join()
        if process.exitcode != 0:
            raise RuntimeError(f"Worker process {process.pid} exited with code {process.exitcode}")

    elapsed = time.perf_counter() - started_at
    return summarize_results(METHOD, started_at, elapsed, results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse web pages in parallel using multiprocessing.")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker processes.")
    parser.add_argument("--url", action="append", dest="urls", help="URL to parse. Can be passed multiple times.")
    args = parser.parse_args()

    result = run_benchmark(urls=args.urls, workers=args.workers)
    print(f"{METHOD}: saved={result['saved']} errors={result['errors']} elapsed={result['elapsed_seconds']:.6f}s", flush=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
