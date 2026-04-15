from __future__ import annotations

import argparse
import multiprocessing
from pathlib import Path

import asyncio_sum
import multiprocessing_sum
import threading_sum
from common_sum import DEFAULT_WORKERS, TARGET_N, format_number, write_benchmark_results


def print_table(results: list[dict[str, object]]) -> None:
    print("| Approach | Chunks | Verified | Time, seconds |")
    print("| --- | ---: | :---: | ---: |")
    for row in results:
        print(
            "| {method} | {chunks} | {verified} | {elapsed:.6f} |".format(
                method=row["method"],
                chunks=row["chunks"],
                verified="yes" if row["verified"] else "no",
                elapsed=row["elapsed_seconds"],
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all Task 1 benchmarks and save report data.")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Number of chunks/subtasks.")
    parser.add_argument("--n", type=int, default=TARGET_N, help="Inclusive upper bound.")
    parser.add_argument("--output-dir", type=Path, default=Path("results"), help="Directory for result files.")
    args = parser.parse_args()

    print(f"Benchmark target: sum 1..{format_number(args.n)}")
    print(f"Subtasks per approach: {args.workers}")
    print()

    results = [
        threading_sum.run_benchmark(workers=args.workers, n=args.n),
        multiprocessing_sum.run_benchmark(workers=args.workers, n=args.n),
        asyncio_sum.run_benchmark(workers=args.workers, n=args.n),
    ]

    print_table(results)
    write_benchmark_results(results, args.output_dir)
    print()
    print(f"Saved Markdown: {args.output_dir / 'task1_benchmark.md'}")
    print(f"Saved JSON: {args.output_dir / 'task1_benchmark.json'}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
