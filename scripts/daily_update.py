#!/usr/bin/env python3
"""Publish one reviewed learning note per India-local calendar day; no third-party packages."""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

LOG = logging.getLogger("daily-journal")
IST = timezone(timedelta(hours=5, minutes=30), "IST")
CATEGORIES = (
    ("python", "Python Programming"),
    ("dsa", "Data Structures and Algorithms"),
    ("javascript", "JavaScript"),
    ("sql", "SQL and Databases"),
    ("git", "Git and GitHub"),
    ("oop", "Object-Oriented Programming"),
    ("backend", "Backend Development"),
    ("rest-api", "REST APIs"),
    ("software-engineering", "Software Engineering Practices"),
    ("interview", "Interview Preparation"),
)
CATEGORY_LABELS = dict(CATEGORIES)
TOPIC_ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
ENTRY_MARKER_RE = re.compile(r"<!-- daily-code-journal: topic_id=([a-z0-9-]+) -->\Z")
AUTO_START = "<!-- DAILY_ENTRIES_START -->"
AUTO_END = "<!-- DAILY_ENTRIES_END -->"


class JournalError(Exception):
    """An actionable, expected validation or publishing error."""


@dataclass(frozen=True)
class Result:
    changed: bool
    reason: str
    topic_id: str = ""
    path: str = ""


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False, newline="\n"
        ) as handle:
            temp_name = handle.name
            handle.write(content)
        os.replace(temp_name, path)
    finally:
        if temp_name is not None and os.path.exists(temp_name):
            os.unlink(temp_name)


def read_json(path: Path) -> object:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise JournalError(f"Cannot load {path}: {exc}") from exc


def require_str(record: dict, key: str, context: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip() or "\r" in value:
        raise JournalError(f"{context}: '{key}' must be nonempty text (without CR).")
    return value.strip()


def read_topics(root: Path) -> list[dict]:
    topics = read_json(root / "content/topics.json")
    if not isinstance(topics, list) or not topics:
        raise JournalError("content/topics.json must contain a nonempty JSON list.")
    seen_ids: set[str] = set()
    result: list[dict] = []
    for index, topic in enumerate(topics, start=1):
        context = f"topic #{index}"
        if not isinstance(topic, dict):
            raise JournalError(f"{context} must be a JSON object.")
        topic_id = require_str(topic, "id", context)
        if not TOPIC_ID_RE.fullmatch(topic_id) or len(topic_id) > 100:
            raise JournalError(f"{context}: invalid id {topic_id!r}; use lowercase slug syntax.")
        if topic_id in seen_ids:
            raise JournalError(f"Duplicate topic ID in library: {topic_id}")
        seen_ids.add(topic_id)
        category = require_str(topic, "category", context)
        if category not in CATEGORY_LABELS:
            raise JournalError(f"{context}: unknown category '{category}'.")
        for key in ("title", "explanation", "code_language", "code", "expected_output", "complexity"):
            require_str(topic, key, context)
        points = topic.get("key_points")
        if not isinstance(points, list) or not 2 <= len(points) <= 6 or any(
            not isinstance(point, str) or not point.strip() for point in points
        ):
            raise JournalError(f"{context}: key_points must have 2–6 nonempty strings.")
        if "```" in topic["code"] or "```" in topic["expected_output"]:
            raise JournalError(f"{context}: code/output may not contain markdown fence delimiters.")
        if "\n" in topic["title"] or "\n" in topic_id:
            raise JournalError(f"{context}: title/ID cannot contain newlines.")
        result.append(topic)
    return result


def read_manifest(root: Path, topics: list[dict]) -> list[dict]:
    manifest = read_json(root / "data/published.json")
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise JournalError("data/published.json must have schema_version: 1.")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise JournalError("data/published.json 'entries' must be a list.")
    lookup = {topic["id"]: topic for topic in topics}
    seen_ids: set[str] = set()
    seen_dates: set[str] = set()
    recorded_files: dict[str, str] = {}
    last_date: date | None = None
    for index, item in enumerate(entries, start=1):
        context = f"manifest entry #{index}"
        if not isinstance(item, dict):
            raise JournalError(f"{context} must be a JSON object.")
        for key in ("topic_id", "date_ist", "title", "category", "path", "generated_at_utc"):
            require_str(item, key, context)
        topic_id = item["topic_id"]
        date_str = item["date_ist"]
        try:
            parsed_date = date.fromisoformat(date_str)
            if parsed_date.isoformat() != date_str:
                raise ValueError("not an ISO date")
            parsed_time = datetime.fromisoformat(item["generated_at_utc"].replace("Z", "+00:00"))
            if parsed_time.tzinfo is None:
                raise ValueError("generated_at_utc must have timezone")
        except ValueError as exc:
            raise JournalError(f"{context} has an invalid date/time: {exc}") from exc
        if last_date is not None and parsed_date <= last_date:
            raise JournalError("Manifest dates must increase strictly; one publication per IST day.")
        last_date = parsed_date
        if topic_id in seen_ids or date_str in seen_dates:
            raise JournalError(f"Manifest has duplicate topic/date: {topic_id} / {date_str}")
        seen_ids.add(topic_id)
        seen_dates.add(date_str)
        topic = lookup.get(topic_id)
        if topic is None:
            raise JournalError(f"Previously published topic '{topic_id}' removed from library; restore it.")
        if item["category"] != topic["category"] or item["title"] != topic["title"]:
            raise JournalError(f"Topic '{topic_id}' metadata changed after publication; retain original metadata.")
        expected_path = f"{topic['category']}/{date_str}--{topic_id}.md"
        if item["path"] != expected_path:
            raise JournalError(f"{context} path must be {expected_path!r}.")
        item_file = root / expected_path
        if not item_file.is_file():
            raise JournalError(f"Published entry missing: {expected_path}. Restore from Git history.")
        with item_file.open("r", encoding="utf-8") as handle:
            first_line = handle.readline().strip()
        if first_line != f"<!-- daily-code-journal: topic_id={topic_id} -->":
            raise JournalError(f"Published entry marker was changed: {expected_path}.")
        recorded_files[expected_path] = topic_id

    # Protect against losing the manifest while generated notes still exist.
    found_files: dict[str, str] = {}
    for category, _ in CATEGORIES:
        for path in (root / category).glob("*.md"):
            with path.open("r", encoding="utf-8") as handle:
                first_line = handle.readline().strip()
            match = ENTRY_MARKER_RE.fullmatch(first_line)
            if match:
                found_files[path.relative_to(root).as_posix()] = match.group(1)
    if found_files != recorded_files:
        extra = sorted(set(found_files) - set(recorded_files))
        missing = sorted(set(recorded_files) - set(found_files))
        raise JournalError(f"Manifest/file mismatch. Untracked notes={extra}; missing notes={missing}.")
    return entries


def select_topic(topics: list[dict], entries: list[dict]) -> dict | None:
    published = {entry["topic_id"] for entry in entries}
    for offset in range(len(CATEGORIES)):
        category = CATEGORIES[(len(entries) + offset) % len(CATEGORIES)][0]
        for topic in topics:
            if topic["category"] == category and topic["id"] not in published:
                return topic
    return None


def render_entry(topic: dict, today: date) -> str:
    topic_id = topic["id"]
    code_lang = topic["code_language"].strip()
    expected_label = "Expected output or usage"
    bullets = "\n".join(f"- {point.strip()}" for point in topic["key_points"])
    return (
        f"<!-- daily-code-journal: topic_id={topic_id} -->\n"
        f"# {topic['title']}\n\n"
        f"**Date (IST):** {today.isoformat()}  \n"
        f"**Category:** {CATEGORY_LABELS[topic['category']]}  \n"
        f"**Publishing method:** Automated from a curated, reviewed topic library.\n\n"
        "## Explanation\n\n"
        f"{topic['explanation'].strip()}\n\n"
        "## Practical example\n\n"
        f"```{code_lang}\n{topic['code'].strip()}\n```\n\n"
        f"## {expected_label}\n\n"
        f"```text\n{topic['expected_output'].strip()}\n```\n\n"
        "## Time and space complexity\n\n"
        f"{topic['complexity'].strip()}\n\n"
        "## Key learning points\n\n"
        f"{bullets}\n\n"
        "---\n\n*Scheduled publication is automated; it does not imply live coding on this date.*\n"
    )


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_index(entries: list[dict], topics: list[dict]) -> str:
    totals = {slug: 0 for slug, _ in CATEGORIES}
    available = {slug: 0 for slug, _ in CATEGORIES}
    for topic in topics:
        available[topic["category"]] += 1
    for entry in entries:
        totals[entry["category"]] += 1
    latest = entries[-1]["date_ist"] if entries else "Not published yet"
    lines = [
        f"**Published topics:** {len(entries)}  ",
        f"**Latest update (IST):** {latest}  ",
        f"**Reviewed library size:** {len(topics)}  ",
        f"**Remaining unpublished topics:** {len(topics) - len(entries)}",
        "",
        "## Categories",
        "",
        "| Category | Published | Available in library |",
        "| --- | ---: | ---: |",
    ]
    lines.extend(
        f"| {label} | {totals[slug]} | {available[slug]} |"
        for slug, label in CATEGORIES
    )
    lines += ["", "## Published learning entries", ""]
    if entries:
        lines += ["| Date (IST) | Category | Topic |", "| --- | --- | --- |"]
        for item in reversed(entries):
            title = escape_cell(item["title"])
            path = item["path"]
            lines.append(
                f"| {item['date_ist']} | {escape_cell(CATEGORY_LABELS[item['category']])} | "
                f"[{title}](<{path}>) |"
            )
    else:
        lines.append("No topics have been published yet. Run the workflow manually to publish the first.")
    return "\n".join(lines) + "\n"


def render_readme(current: str, entries: list[dict], topics: list[dict]) -> str:
    if current.count(AUTO_START) != 1 or current.count(AUTO_END) != 1:
        raise JournalError("README.md needs exactly one START and one END marker.")
    start = current.index(AUTO_START) + len(AUTO_START)
    end = current.index(AUTO_END)
    if start >= end:
        raise JournalError("README.md automatic region markers are misordered.")
    return current[:start] + "\n" + render_index(entries, topics) + current[end:]


def write_action_output(result: Result) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"changed={'true' if result.changed else 'false'}\n")
            handle.write(f"topic_id={result.topic_id}\n")
            handle.write(f"path={result.path}\n")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(f"### Daily code journal\n\n{result.reason}\n")


def run(root: Path, today: date, *, dry_run: bool = False, validate_only: bool = False) -> Result:
    topics = read_topics(root)
    entries = read_manifest(root, topics)
    readme_path = root / "README.md"
    try:
        current_readme = readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise JournalError(f"Cannot read {readme_path}: {exc}") from exc
    # Always validate marker integrity, even when no publication is needed.
    render_readme(current_readme, entries, topics)
    if validate_only:
        return Result(False, f"Validation passed: {len(topics)} reviewed topics; {len(entries)} published.")
    if entries and entries[-1]["date_ist"] == today.isoformat():
        return Result(False, f"Already published an entry for {today.isoformat()} IST; no changes.")
    if entries and today < date.fromisoformat(entries[-1]["date_ist"]):
        raise JournalError("Current IST date precedes the last publication date; refusing to backdate.")
    topic = select_topic(topics, entries)
    if topic is None:
        return Result(False, "Reviewed library exhausted: no entry published. Add unique topics to content/topics.json.")
    relative = f"{topic['category']}/{today.isoformat()}--{topic['id']}.md"
    destination = root / relative
    if destination.exists():
        raise JournalError(f"Refusing to overwrite existing file {relative}. Resolve the collision manually.")
    message = f"Publish {topic['title']} ({today.isoformat()} IST) at {relative}."
    if dry_run:
        return Result(False, "Dry run only: " + message, topic["id"], relative)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    entry = {
        "topic_id": topic["id"],
        "date_ist": today.isoformat(),
        "title": topic["title"],
        "category": topic["category"],
        "path": relative,
        "generated_at_utc": now,
    }
    next_entries = [*entries, entry]
    next_readme = render_readme(current_readme, next_entries, topics)
    next_manifest = json.dumps({"schema_version": 1, "entries": next_entries}, indent=2, ensure_ascii=False) + "\n"
    atomic_write(destination, render_entry(topic, today))
    atomic_write(root / "data/published.json", next_manifest)
    atomic_write(readme_path, next_readme)
    return Result(True, message, topic["id"], relative)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Show next topic; do not write anything")
    mode.add_argument("--validate", action="store_true", help="Validate library and published entries only")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Repository root (primarily for testing)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        now_utc = datetime.now(timezone.utc)
        today_ist = now_utc.astimezone(IST).date()
        LOG.info("Current UTC: %s; current IST date: %s", now_utc.isoformat(), today_ist)
        result = run(args.root.resolve(), today_ist, dry_run=args.dry_run, validate_only=args.validate)
        LOG.info(result.reason)
        write_action_output(result)
        return 0
    except (JournalError, OSError) as exc:
        LOG.error("Publication failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
