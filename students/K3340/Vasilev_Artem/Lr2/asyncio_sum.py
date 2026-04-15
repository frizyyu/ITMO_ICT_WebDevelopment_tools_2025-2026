from __future__ import annotations

import argparse
import asyncio
import time

from common_sum import DEFAULT_WORKERS, TARGET_N, arithmetic_progression_sum, make_chunks
from common_sum import print_result, verify_total


async def calculate_sum(start: int, end: int) -> int:
    await asyncio.sleep(0)
    return arithmetic_progression_sum(start, end)


async def run_benchmark_async(workers: int = DEFAULT_WORKERS, n: int = TARGET_N) -> dict[str, object]:
    chunks = make_chunks(1, n, workers)

    started_at = time.perf_counter()
    tasks = [calculate_sum(start, end) for start, end in chunks]
    results = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - started_at

    total = sum(results)
    return {
        "method": "asyncio",
        "chunks": len(chunks),
        "result": total,
        "verified": verify_total(total, n),
        "elapsed_seconds": elapsed,
    }


def run_benchmark(workers: int = DEFAULT_WORKERS, n: int = TARGET_N) -> dict[str, object]:
    return asyncio.run(run_benchmark_async(workers=workers, n=n))


def main() -> None:
    parser = argparse.ArgumentParser(description="Sum 1..N using asyncio orchestration.")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Number of chunks/async tasks.")
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
