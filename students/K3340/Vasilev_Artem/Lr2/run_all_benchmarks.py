from __future__ import annotations

import json
import multiprocessing
from pathlib import Path

import asyncio_parse
import multiprocessing_parse
import multiprocessing_sum
import threading_parse
import threading_sum
from asyncio_sum import run_benchmark as run_asyncio_sum_benchmark
from common_parse import DEFAULT_URLS, create_db_engine, print_benchmark_table, write_task2_results
from common_sum import DEFAULT_WORKERS as SUM_WORKERS
from common_sum import TARGET_N, format_number, write_benchmark_results
from sqlalchemy import text

RESULTS_DIR = Path("results")


def get_lr2_tasks_count() -> int | None:
    try:
        engine = create_db_engine()
        with engine.connect() as connection:
            return int(
                connection.scalar(
                    text("select count(*) from tasks where description like '%LR2 parser source:%'")
                )
                or 0
            )
    except Exception as exc:
        print(f"Could not read parsed_pages count: {exc}", flush=True)
        return None
    finally:
        try:
            engine.dispose()
        except UnboundLocalError:
            pass


def write_summary(task1_results: list[dict[str, object]], task2_results: list[dict[str, object]]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    db_count = get_lr2_tasks_count()

    summary = {
        "task1": task1_results,
        "task2": task2_results,
        "lr2_tasks_count": db_count,
    }

    (RESULTS_DIR / "lr2_benchmark_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# LR2 Benchmark Summary",
        "",
        "## Task 1",
        "",
        f"Target range: `1..{format_number(TARGET_N)}`",
        "",
        "| Approach | Chunks | Verified | Time, seconds |",
        "| --- | ---: | :---: | ---: |",
    ]
    for row in task1_results:
        lines.append(
            "| {method} | {chunks} | {verified} | {elapsed:.6f} |".format(
                method=row["method"],
                chunks=row["chunks"],
                verified="yes" if row["verified"] else "no",
                elapsed=row["elapsed_seconds"],
            )
        )

    lines.extend(
        [
            "",
            "## Task 2",
            "",
            f"URLs parsed: `{len(DEFAULT_URLS)}`",
            "",
            "| Approach | URLs | Saved tasks | Errors | Time, seconds |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in task2_results:
        lines.append(
            "| {method} | {urls} | {saved} | {errors} | {elapsed:.6f} |".format(
                method=row["method"],
                urls=row["urls"],
                saved=row["saved"],
                errors=row["errors"],
                elapsed=row["elapsed_seconds"],
            )
        )

    lines.extend(
        [
            "",
            "## Database",
            "",
            f"`tasks` rows created/updated by LR2 parsers: `{db_count if db_count is not None else 'unknown'}`",
        ]
    )

    (RESULTS_DIR / "lr2_benchmark_summary.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    print("Running LR2 benchmarks", flush=True)
    print(f"Task 1 target: 1..{format_number(TARGET_N)}", flush=True)
    print(f"Task 1 chunks: {SUM_WORKERS}", flush=True)
    print(f"Task 2 URLs: {len(DEFAULT_URLS)}", flush=True)
    print()

    task1_results = [
        threading_sum.run_benchmark(workers=SUM_WORKERS, n=TARGET_N),
        multiprocessing_sum.run_benchmark(workers=SUM_WORKERS, n=TARGET_N),
        run_asyncio_sum_benchmark(workers=SUM_WORKERS, n=TARGET_N),
    ]
    write_benchmark_results(task1_results, RESULTS_DIR)

    print("Task 1 finished", flush=True)
    print()

    task2_results = [
        threading_parse.run_benchmark(urls=DEFAULT_URLS, workers=4),
        multiprocessing_parse.run_benchmark(urls=DEFAULT_URLS, workers=4),
        asyncio_parse.run_benchmark(urls=DEFAULT_URLS, workers=4),
    ]
    write_task2_results(task2_results, RESULTS_DIR)

    print()
    print("Task 2 finished", flush=True)
    print_benchmark_table(task2_results)

    write_summary(task1_results, task2_results)
    print()
    print(f"Saved summary Markdown: {RESULTS_DIR / 'lr2_benchmark_summary.md'}", flush=True)
    print(f"Saved summary JSON: {RESULTS_DIR / 'lr2_benchmark_summary.json'}", flush=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
