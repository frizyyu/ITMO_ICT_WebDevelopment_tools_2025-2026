from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

TARGET_N = 10_000_000_000_000
DEFAULT_WORKERS = min(os.cpu_count() or 4, 8)


def arithmetic_progression_sum(start: int, end: int) -> int:
    if start > end:
        return 0
    count = end - start + 1
    return (start + end) * count // 2


def expected_sum(n: int = TARGET_N) -> int:
    return n * (n + 1) // 2


def make_chunks(start: int, end: int, chunk_count: int) -> list[tuple[int, int]]:
    if chunk_count < 1:
        raise ValueError("chunk_count must be positive")
    if start > end:
        return []

    total_numbers = end - start + 1
    actual_chunks = min(chunk_count, total_numbers)
    base_size, remainder = divmod(total_numbers, actual_chunks)

    chunks: list[tuple[int, int]] = []
    chunk_start = start
    for index in range(actual_chunks):
        chunk_size = base_size + (1 if index < remainder else 0)
        chunk_end = chunk_start + chunk_size - 1
        chunks.append((chunk_start, chunk_end))
        chunk_start = chunk_end + 1

    return chunks


def verify_total(total: int, n: int = TARGET_N) -> bool:
    return total == expected_sum(n)


def format_number(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def print_result(method: str, total: int, elapsed_seconds: float, chunks: int, n: int = TARGET_N) -> None:
    reference = expected_sum(n)
    is_valid = total == reference

    print(f"Method: {method}")
    print(f"Range: 1..{format_number(n)}")
    print(f"Chunks: {chunks}")
    print(f"Result: {format_number(total)}")
    print(f"Expected: {format_number(reference)}")
    print(f"Verified: {'yes' if is_valid else 'no'}")
    print(f"Elapsed: {elapsed_seconds:.6f} seconds")


def write_benchmark_results(results: Iterable[dict[str, object]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = list(results)

    markdown_lines = [
        "# Task 1 Benchmark Results",
        "",
        "| Approach | Chunks | Verified | Time, seconds | Result |",
        "| --- | ---: | :---: | ---: | ---: |",
    ]

    for row in rows:
        markdown_lines.append(
            "| {method} | {chunks} | {verified} | {elapsed:.6f} | {result} |".format(
                method=row["method"],
                chunks=row["chunks"],
                verified="yes" if row["verified"] else "no",
                elapsed=row["elapsed_seconds"],
                result=format_number(int(row["result"])),
            )
        )

    (output_dir / "task1_benchmark.md").write_text(
        "\n".join(markdown_lines) + "\n",
        encoding="utf-8",
    )
    (output_dir / "task1_benchmark.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
