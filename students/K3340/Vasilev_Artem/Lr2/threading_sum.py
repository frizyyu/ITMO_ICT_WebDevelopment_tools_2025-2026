from __future__ import annotations

import argparse
import threading
import time

from common_sum import DEFAULT_WORKERS, TARGET_N, arithmetic_progression_sum, make_chunks
from common_sum import print_result, verify_total


def calculate_sum(start: int, end: int) -> int:
    return arithmetic_progression_sum(start, end)


def _worker(index: int, start: int, end: int, results: list[int]) -> None:
    results[index] = calculate_sum(start, end)


def run_benchmark(workers: int = DEFAULT_WORKERS, n: int = TARGET_N) -> dict[str, object]:
    chunks = make_chunks(1, n, workers)
    results = [0] * len(chunks)
    threads: list[threading.Thread] = []

    started_at = time.perf_counter()
    for index, (start, end) in enumerate(chunks):
        thread = threading.Thread(target=_worker, args=(index, start, end, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(results)
    elapsed = time.perf_counter() - started_at

    return {
        "method": "threading",
        "chunks": len(chunks),
        "result": total,
        "verified": verify_total(total, n),
        "elapsed_seconds": elapsed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sum 1..N using Python threading.")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Number of chunks/threads.")
    parser.add_argument("--n", type=int, default=TARGET_N, help="Inclusive upper bound.")
    args = parser.parse_args()

    result = run_benchmark(workers=args.workers, n=args.n)
    print_result(
        method=str(result["method"]),
        total=int(result["result"]),
        elapsed_seconds=float(result["elapsed_seconds"]),
        chunks=int(result["chunks"]),
        n=args.n,
    )


if __name__ == "__main__":
    main()
