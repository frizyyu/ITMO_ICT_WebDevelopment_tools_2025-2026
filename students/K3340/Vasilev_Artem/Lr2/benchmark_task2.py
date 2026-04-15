from __future__ import annotations

import argparse
import multiprocessing
from pathlib import Path

import asyncio_parse
import multiprocessing_parse
import threading_parse
from common_parse import DEFAULT_URLS, print_benchmark_table, write_task2_results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all Task 2 parsers and save benchmark results.")
    parser.add_argument("--workers", type=int, default=4, help="Number of chunks/workers per approach.")
    parser.add_argument("--url", action="append", dest="urls", help="URL to parse. Can be passed multiple times.")
    parser.add_argument("--output-dir", type=Path, default=Path("results"), help="Directory for result files.")
    args = parser.parse_args()

    urls = args.urls or DEFAULT_URLS
    print(f"Task 2 benchmark: {len(urls)} URLs, {args.workers} workers/chunks", flush=True)
    print(flush=True)

    results = [
        threading_parse.run_benchmark(urls=urls, workers=args.workers),
        multiprocessing_parse.run_benchmark(urls=urls, workers=args.workers),
        asyncio_parse.run_benchmark(urls=urls, workers=args.workers),
    ]

    print(flush=True)
    print_benchmark_table(results)
    write_task2_results(results, args.output_dir)
    print(flush=True)
    print(f"Saved Markdown: {args.output_dir / 'task2_benchmark.md'}", flush=True)
    print(f"Saved JSON: {args.output_dir / 'task2_benchmark.json'}", flush=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
