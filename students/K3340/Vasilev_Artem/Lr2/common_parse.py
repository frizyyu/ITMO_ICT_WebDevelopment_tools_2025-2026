from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from sqlalchemy import Boolean, Column, DateTime, Integer, MetaData, String, Table, Text
from sqlalchemy import create_engine, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Engine

REQUEST_TIMEOUT_SECONDS = 15
MAX_PROJECTS_PER_SOURCE = 5
ROOT_DIR = Path(__file__).resolve().parent
LR1_LAB_DIR = ROOT_DIR.parent / "Lr1" / "lab"
RESULTS_DIR = ROOT_DIR / "results"
PARSER_USERNAME = "parser_bot"
PARSER_EMAIL = "parser_bot@example.local"
PARSER_PASSWORD_HASH = "lr2-parser-no-login"
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ITMO-LR2-project-parser/1.0)"}

DEFAULT_URLS = [
    "https://www.peopleperhour.com/freelance-jobs/technology-programming",
    "https://www.peopleperhour.com/freelance-jobs/technology-programming/programming-coding",
    "https://www.peopleperhour.com/freelance-jobs/technology-programming/website-development",
    "https://www.peopleperhour.com/freelance-jobs/technology-programming/e-commerce-cms-development",
    "https://www.peopleperhour.com/freelance-jobs/artificial-intelligence/artificial-intelligence-agent-development",
    "https://www.peopleperhour.com/freelance-jobs/artificial-intelligence/artificial-intelligence-website-development",
]

metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), nullable=False),
    Column("email", String(255), nullable=False),
    Column("hashed_password", String(255), nullable=False),
    Column("full_name", String(255)),
    Column("bio", Text),
    Column("is_active", Boolean),
)

categories_table = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("description", Text),
    Column("color", String(20)),
    Column("owner_id", Integer, nullable=False),
)

tasks_table = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(255), nullable=False),
    Column("description", Text),
    Column("priority", postgresql.ENUM("low", "medium", "high", "urgent", name="task_priority", create_type=False), nullable=False),
    Column(
        "status",
        postgresql.ENUM("pending", "in_progress", "completed", "cancelled", "overdue", name="task_status", create_type=False),
        nullable=False,
    ),
    Column("estimated_minutes", Integer),
    Column("due_at", DateTime(timezone=True)),
    Column("completed_at", DateTime(timezone=True)),
    Column("owner_id", Integer, nullable=False),
)

task_categories_table = Table(
    "task_categories",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("task_id", Integer, nullable=False),
    Column("category_id", Integer, nullable=False),
    Column("label", String(100)),
)


@dataclass(frozen=True)
class ProjectItem:
    source_url: str
    project_url: str
    title: str
    description: str
    category: str
    budget: str | None = None
    meta: str | None = None


@dataclass(frozen=True)
class ParseResult:
    url: str
    title: str | None
    parsed_by: str
    status: str
    extracted_count: int = 0
    saved_count: int = 0
    error: str | None = None


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def get_database_url() -> str:
    candidates = [
        os.getenv("DATABASE_URL"),
        read_env_file(ROOT_DIR / ".env").get("DATABASE_URL"),
        read_env_file(LR1_LAB_DIR / ".env").get("DATABASE_URL"),
        read_env_file(LR1_LAB_DIR / ".env.example").get("DATABASE_URL"),
    ]

    for candidate in candidates:
        if candidate:
            return normalize_database_url(candidate)

    return "postgresql+psycopg://postgres:postgres@localhost:5432/time_manager"


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def create_db_engine() -> Engine:
    return create_engine(get_database_url(), pool_pre_ping=True)


def clean_text(value: str) -> str:
    return " ".join(value.split())


def node_text(node) -> str:
    return clean_text(node.get_text(" ", strip=True)) if node else ""


def page_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return clean_text(soup.title.string)
    heading = soup.find("h1")
    if heading:
        return node_text(heading)
    return "Untitled source"


def source_category(url: str) -> str:
    path = urlparse(url).path.lower()
    if "freelancer.com" in url:
        if "web-scraping" in path:
            return "Freelancer Web Scraping"
        if "django" in path:
            return "Freelancer Django"
        return "Freelancer Python"
    if "guru.com" in url:
        if "web-scraping" in path or "data-scraping" in path:
            return "Guru Web Scraping"
        if "web-development" in path:
            return "Guru Web Development"
        if "javascript" in path:
            return "Guru JavaScript"
        if "api" in path:
            return "Guru API Development"
        return "Guru Python"
    if "peopleperhour.com" in url:
        if "programming-coding" in path:
            return "PeoplePerHour Programming"
        if "website-development" in path:
            return "PeoplePerHour Website Development"
        if "e-commerce-cms-development" in path:
            return "PeoplePerHour E-Commerce"
        if "artificial-intelligence-agent-development" in path:
            return "PeoplePerHour AI Agents"
        if "artificial-intelligence-website-development" in path:
            return "PeoplePerHour AI Websites"
        return "PeoplePerHour Technology"
    return "Parsed Freelance Projects"


def parse_project_items(url: str, html: str, limit: int = MAX_PROJECTS_PER_SOURCE) -> list[ProjectItem]:
    soup = BeautifulSoup(html, "html.parser")
    if "freelancer.com" in url:
        return parse_freelancer_projects(url, soup, limit)
    if "guru.com" in url:
        return parse_guru_projects(url, soup, limit)
    if "peopleperhour.com" in url:
        return parse_peopleperhour_projects(url, soup, limit)
    return []


def parse_freelancer_projects(url: str, soup: BeautifulSoup, limit: int) -> list[ProjectItem]:
    items: list[ProjectItem] = []
    category = source_category(url)
    for card in soup.select(".JobSearchCard-item"):
        title_node = card.select_one(".JobSearchCard-primary-heading-link")
        title = node_text(title_node)
        if not title:
            continue

        project_url = urljoin(url, title_node.get("href", "")) if title_node else url
        description = node_text(card.select_one(".JobSearchCard-primary-description"))
        budget = node_text(card.select_one(".JobSearchCard-primary-price")) or None
        tags = [node_text(tag) for tag in card.select(".JobSearchCard-primary-tagsLink")[:8]]
        meta = ", ".join(tag for tag in tags if tag) or None
        items.append(
            ProjectItem(
                source_url=url,
                project_url=project_url,
                title=title,
                description=description,
                category=category,
                budget=budget,
                meta=meta,
            )
        )
        if len(items) >= limit:
            break
    return items


def parse_guru_projects(url: str, soup: BeautifulSoup, limit: int) -> list[ProjectItem]:
    items: list[ProjectItem] = []
    category = source_category(url)
    for card in soup.select(".jobRecord"):
        title_node = card.select_one(".jobRecord__title")
        title = node_text(title_node)
        if not title:
            continue

        link = title_node.select_one("a[href]") if title_node else None
        project_url = urljoin(url, link.get("href", "")) if link else url
        description = node_text(card.select_one(".jobRecord__desc"))
        budget = node_text(card.select_one(".jobRecord__budget")) or None
        meta = node_text(card.select_one(".jobRecord__meta")) or None
        items.append(
            ProjectItem(
                source_url=url,
                project_url=project_url,
                title=title,
                description=description,
                category=category,
                budget=budget,
                meta=meta,
            )
        )
        if len(items) >= limit:
            break
    return items


def parse_peopleperhour_projects(url: str, soup: BeautifulSoup, limit: int) -> list[ProjectItem]:
    items: list[ProjectItem] = []
    seen_urls: set[str] = set()
    category = source_category(url)
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        title = node_text(link)
        if len(title) < 25 or "freelance-jobs" not in href:
            continue
        if href.startswith("/freelance-jobs/"):
            continue

        project_url = urljoin(url, href)
        if project_url in seen_urls:
            continue
        seen_urls.add(project_url)

        container = link
        for _ in range(4):
            if container.parent is None:
                break
            container = container.parent
        container_text = node_text(container)
        description = container_text if len(container_text) > len(title) else title
        budget = extract_budget(container_text)
        items.append(
            ProjectItem(
                source_url=url,
                project_url=project_url,
                title=title,
                description=description,
                category=category,
                budget=budget,
                meta="PeoplePerHour public project card",
            )
        )
        if len(items) >= limit:
            break
    return items


def extract_budget(text_value: str) -> str | None:
    match = re.search(r"([$€£]\s?\d+(?:[.,]\d+)?)", text_value)
    return match.group(1) if match else None


def save_projects(projects: list[ProjectItem], parsed_by: str, engine: Engine | None = None) -> int:
    if not projects:
        return 0

    own_engine = engine is None
    engine = engine or create_db_engine()
    saved_count = 0

    with engine.begin() as connection:
        if engine.dialect.name == "postgresql":
            connection.execute(text("SELECT pg_advisory_xact_lock(20250203)"))

        owner_id = ensure_parser_user(connection)
        category_ids: dict[str, int] = {}

        for project in projects:
            category_id = category_ids.get(project.category)
            if category_id is None:
                category_id = ensure_category(connection, owner_id, project.category)
                category_ids[project.category] = category_id

            task_id = upsert_task(connection, owner_id, project, parsed_by)
            ensure_task_category(connection, task_id, category_id, parsed_by)
            saved_count += 1

    if own_engine:
        engine.dispose()
    return saved_count


def ensure_parser_user(connection) -> int:
    user_id = connection.scalar(
        select(users_table.c.id).where(users_table.c.username == PARSER_USERNAME)
    )
    if user_id is not None:
        return int(user_id)

    return int(
        connection.execute(
            users_table.insert()
            .values(
                username=PARSER_USERNAME,
                email=PARSER_EMAIL,
                hashed_password=PARSER_PASSWORD_HASH,
                full_name="LR2 Parser Bot",
                bio="Technical user created by LR2 parsers.",
                is_active=True,
            )
            .returning(users_table.c.id)
        ).scalar_one()
    )


def ensure_category(connection, owner_id: int, name: str) -> int:
    category_id = connection.scalar(
        select(categories_table.c.id).where(
            categories_table.c.owner_id == owner_id,
            categories_table.c.name == name[:100],
        )
    )
    if category_id is not None:
        return int(category_id)

    return int(
        connection.execute(
            categories_table.insert()
            .values(
                name=name[:100],
                description="Category created from parsed freelance project sources.",
                color="#3B82F6",
                owner_id=owner_id,
            )
            .returning(categories_table.c.id)
        ).scalar_one()
    )


def upsert_task(connection, owner_id: int, project: ProjectItem, parsed_by: str) -> int:
    source_id = build_source_id(project, parsed_by)
    description = build_task_description(project, parsed_by, source_id)
    existing_task_id = connection.scalar(
        select(tasks_table.c.id).where(
            tasks_table.c.owner_id == owner_id,
            tasks_table.c.description.like(f"%Source ID: {source_id}%"),
        )
    )

    values = {
        "title": project.title[:255],
        "description": description,
        "priority": "medium",
        "status": "pending",
        "estimated_minutes": 60,
        "owner_id": owner_id,
    }

    if existing_task_id is None:
        return int(
            connection.execute(
                tasks_table.insert().values(**values).returning(tasks_table.c.id)
            ).scalar_one()
        )

    connection.execute(
        tasks_table.update()
        .where(tasks_table.c.id == existing_task_id)
        .values(**values)
    )
    return int(existing_task_id)


def ensure_task_category(connection, task_id: int, category_id: int, parsed_by: str) -> None:
    link_id = connection.scalar(
        select(task_categories_table.c.id).where(
            task_categories_table.c.task_id == task_id,
            task_categories_table.c.category_id == category_id,
        )
    )
    if link_id is not None:
        return

    connection.execute(
        task_categories_table.insert().values(
            task_id=task_id,
            category_id=category_id,
            label=f"parsed:{parsed_by}"[:100],
        )
    )


def build_source_id(project: ProjectItem, parsed_by: str) -> str:
    return f"lr2:{parsed_by}:{project.project_url}"


def build_task_description(project: ProjectItem, parsed_by: str, source_id: str) -> str:
    parts = [
        "LR2 parser source: freelance project card",
        f"Source ID: {source_id}",
        f"Parser: {parsed_by}",
        f"Source page: {project.source_url}",
        f"Project URL: {project.project_url}",
    ]
    if project.budget:
        parts.append(f"Budget: {project.budget}")
    if project.meta:
        parts.append(f"Meta: {project.meta}")
    if project.description:
        parts.extend(["", "Parsed description:", project.description])
    return "\n".join(parts)


def chunk_urls(urls: list[str], chunk_count: int) -> list[list[str]]:
    if chunk_count < 1:
        raise ValueError("chunk_count must be positive")
    if not urls:
        return []

    actual_chunks = min(chunk_count, len(urls))
    chunks = [[] for _ in range(actual_chunks)]
    for index, url in enumerate(urls):
        chunks[index % actual_chunks].append(url)
    return chunks


def print_parse_result(result: ParseResult) -> None:
    if result.status == "ok":
        print(
            f"[{result.parsed_by}] OK {result.url} -> "
            f"extracted={result.extracted_count}, saved_tasks={result.saved_count}",
            flush=True,
        )
    else:
        print(f"[{result.parsed_by}] ERROR {result.url} -> {result.error}", flush=True)


def print_benchmark_table(results: list[dict[str, object]]) -> None:
    print("| Approach | URLs | Saved tasks | Errors | Time, seconds |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for row in results:
        print(
            "| {method} | {urls} | {saved} | {errors} | {elapsed:.6f} |".format(
                method=row["method"],
                urls=row["urls"],
                saved=row["saved"],
                errors=row["errors"],
                elapsed=row["elapsed_seconds"],
            )
        )


def write_task2_results(results: Iterable[dict[str, object]], output_dir: Path = RESULTS_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = list(results)

    markdown_lines = [
        "# Task 2 Benchmark Results",
        "",
        "| Approach | URLs | Saved tasks | Errors | Time, seconds |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        markdown_lines.append(
            "| {method} | {urls} | {saved} | {errors} | {elapsed:.6f} |".format(
                method=row["method"],
                urls=row["urls"],
                saved=row["saved"],
                errors=row["errors"],
                elapsed=row["elapsed_seconds"],
            )
        )

    (output_dir / "task2_benchmark.md").write_text(
        "\n".join(markdown_lines) + "\n",
        encoding="utf-8",
    )
    (output_dir / "task2_benchmark.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def summarize_results(method: str, started_at: float, elapsed_seconds: float, results: list[ParseResult]) -> dict[str, object]:
    return {
        "method": method,
        "started_at": started_at,
        "urls": len(results),
        "saved": sum(result.saved_count for result in results),
        "extracted": sum(result.extracted_count for result in results),
        "ok": sum(1 for result in results if result.status == "ok"),
        "errors": sum(1 for result in results if result.status != "ok"),
        "elapsed_seconds": elapsed_seconds,
        "items": [asdict(result) for result in results],
    }
