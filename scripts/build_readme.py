#!/usr/bin/env python3
"""Generate the README paper index from data/papers.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "papers.json"
README_PATH = ROOT / "README.md"
STATS_START = "<!-- GENERATED_STATS_START -->"
STATS_END = "<!-- GENERATED_STATS_END -->"
LISTS_START = "<!-- GENERATED_PAPER_LISTS_START -->"
LISTS_END = "<!-- GENERATED_PAPER_LISTS_END -->"


def load_data() -> dict:
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def replace_block(text: str, start: str, end: str, body: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"Expected exactly one marker pair: {start}, {end}")
    before, remainder = text.split(start, 1)
    _, after = remainder.split(end, 1)
    return f"{before}{start}\n{body.rstrip()}\n{end}{after}"


def escape_cell(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", " ").strip()


def render_resources(paper: dict) -> str:
    resources = []
    if paper.get("project"):
        resources.append(f"[Project]({paper['project']})")
    if paper.get("code"):
        resources.append(f"[Code]({paper['code']})")
    return " / ".join(resources) if resources else "-"


def render_paper_lists(data: dict) -> str:
    sections = []
    for index, line in enumerate(data["lines"], start=1):
        papers = line["papers"]
        rows = [
            f"## {index}. {line['title']}",
            "",
            line["description"],
            "",
            f"**Deployment-time update:** {line['changes']}",
            "",
            f"**Core advantage:** {line['strength']}",
            "",
            f"**Main limitation:** {line['limitation']}",
            "",
            f"**Papers ({len(papers)})**",
            "",
            "| Date | Paper | Venue | Resources | Tags |",
            "| --- | --- | --- | --- | --- |",
        ]
        for paper in papers:
            title = escape_cell(paper["title"])
            tags = ", ".join(escape_cell(tag) for tag in paper.get("tags", []))
            rows.append(
                "| {date} | [{title}]({url}) | `{venue}` | {resources} | {tags} |".format(
                    date=paper["date"],
                    title=title,
                    url=paper["paper"],
                    venue=escape_cell(paper["venue"]),
                    resources=render_resources(paper),
                    tags=tags or "-",
                )
            )
        sections.append("\n".join(rows))
    return "\n\n".join(sections)


def render_stats(data: dict) -> str:
    count = sum(len(line["papers"]) for line in data["lines"])
    return (
        f"**{count} papers across {len(data['lines'])} lines of work.** "
        f"Last updated: `{data['last_updated']}`."
    )


def build_readme(data: dict, current: str) -> str:
    rendered = replace_block(
        current, STATS_START, STATS_END, render_stats(data)
    )
    return replace_block(
        rendered, LISTS_START, LISTS_END, render_paper_lists(data)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when README.md is not synchronized with the data file.",
    )
    args = parser.parse_args()

    data = load_data()
    current = README_PATH.read_text(encoding="utf-8")
    expected = build_readme(data, current)

    if args.check:
        if current != expected:
            print("README.md is stale. Run: python3 scripts/build_readme.py")
            return 1
        print("README.md is synchronized with data/papers.json.")
        return 0

    README_PATH.write_text(expected, encoding="utf-8")
    print("Updated README.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
