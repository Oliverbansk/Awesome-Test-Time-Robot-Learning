#!/usr/bin/env python3
"""Validate the machine-readable paper index."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "papers.json"
LINE_FIELDS = {
    "id",
    "title",
    "description",
    "changes",
    "strength",
    "limitation",
    "papers",
}
PAPER_FIELDS = {"date", "title", "venue", "paper", "tags"}


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def main() -> int:
    with DATA_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)

    errors: list[str] = []
    seen_line_ids: set[str] = set()
    seen_titles: set[str] = set()
    seen_urls: set[str] = set()
    paper_count = 0

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    try:
        date.fromisoformat(data["last_updated"])
    except (KeyError, TypeError, ValueError):
        errors.append("last_updated must be an ISO date")

    lines = data.get("lines")
    if not isinstance(lines, list) or not lines:
        errors.append("lines must be a non-empty list")
        lines = []

    for line_index, line in enumerate(lines):
        location = f"lines[{line_index}]"
        missing = LINE_FIELDS - line.keys()
        if missing:
            errors.append(f"{location} missing fields: {sorted(missing)}")
            continue

        line_id = line["id"]
        if line_id in seen_line_ids:
            errors.append(f"duplicate line id: {line_id}")
        seen_line_ids.add(line_id)

        previous_date: date | None = None
        for paper_index, paper in enumerate(line["papers"]):
            paper_count += 1
            paper_location = f"{location}.papers[{paper_index}]"
            missing = PAPER_FIELDS - paper.keys()
            if missing:
                errors.append(
                    f"{paper_location} missing fields: {sorted(missing)}"
                )
                continue

            try:
                release_date = date.fromisoformat(paper["date"])
            except (TypeError, ValueError):
                errors.append(f"{paper_location}.date is not an ISO date")
                continue

            if previous_date and release_date < previous_date:
                errors.append(
                    f"{location} is not sorted oldest to newest at "
                    f"{paper['title']}"
                )
            previous_date = release_date

            title_key = paper["title"].casefold().strip()
            if title_key in seen_titles:
                errors.append(f"duplicate paper title: {paper['title']}")
            seen_titles.add(title_key)

            paper_url = paper["paper"].strip()
            if not is_url(paper_url):
                errors.append(f"invalid paper URL: {paper_url}")
            if paper_url in seen_urls:
                errors.append(f"duplicate paper URL: {paper_url}")
            seen_urls.add(paper_url)

            if not paper["venue"].strip():
                errors.append(f"empty venue for: {paper['title']}")
            if not isinstance(paper["tags"], list):
                errors.append(f"tags must be a list for: {paper['title']}")

            for field in ("project", "code"):
                if paper.get(field) and not is_url(paper[field]):
                    errors.append(
                        f"invalid {field} URL for {paper['title']}: "
                        f"{paper[field]}"
                    )

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {paper_count} papers across {len(lines)} lines of work."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
