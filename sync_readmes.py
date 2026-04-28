#!/usr/bin/env python3
"""
sync_readmes.py — Pull Confluence pages and write README.md for each project.

Usage:
    python sync_readmes.py                  # sync all projects
    python sync_readmes.py --project 755    # sync one project
    python sync_readmes.py --dry-run        # preview without writing

Requires .env with:
    CONFLUENCE_EMAIL=you@ucsd.edu
    API_KEY=your-api-token
"""

import os
import re
import sys
import argparse
from html.parser import HTMLParser
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv(Path(__file__).parent / ".env")

CONFLUENCE_BASE = "https://ucsdcollab.atlassian.net/wiki"
SPACE_KEY = "IPPS"
EMAIL = os.environ.get("CONFLUENCE_EMAIL", "")
API_KEY = os.environ.get("API_KEY", "")


# ---------------------------------------------------------------------------
# Confluence HTML → Markdown converter
# ---------------------------------------------------------------------------

class _MarkdownConverter(HTMLParser):
    """Converts Confluence storage-format HTML to Markdown."""

    BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
                  "ul", "ol", "li", "pre", "blockquote", "tr", "thead", "tbody"}

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._tag_stack: list[str] = []
        self._list_stack: list[str] = []   # "ul" or "ol"
        self._ol_counters: list[int] = []
        self._in_pre = False
        self._in_code = False
        self._skip_depth = 0               # depth inside skipped Confluence macros
        self._link_href: str | None = None
        self._link_text_parts: list[str] = []

    # ------------------------------------------------------------------
    def handle_starttag(self, tag: str, attrs: list):
        tag = tag.lower()
        attr = dict(attrs)

        if self._skip_depth or tag.startswith("ac:") or tag.startswith("ri:"):
            self._skip_depth += 1
            return

        self._tag_stack.append(tag)

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self._flush_inline()
            self._parts.append(f"\n\n{'#' * level} ")
        elif tag == "p":
            self._flush_inline()
            self._parts.append("\n\n")
        elif tag == "br":
            self._parts.append("  \n")
        elif tag == "ul":
            self._list_stack.append("ul")
        elif tag == "ol":
            self._list_stack.append("ol")
            self._ol_counters.append(0)
        elif tag == "li":
            self._flush_inline()
            depth = len(self._list_stack) - 1
            indent = "  " * depth
            if self._list_stack and self._list_stack[-1] == "ol":
                self._ol_counters[-1] += 1
                bullet = f"{self._ol_counters[-1]}."
            else:
                bullet = "-"
            self._parts.append(f"\n{indent}{bullet} ")
        elif tag == "pre":
            self._in_pre = True
            self._flush_inline()
            self._parts.append("\n\n```\n")
        elif tag == "code" and not self._in_pre:
            self._in_code = True
            self._parts.append("`")
        elif tag in ("strong", "b"):
            self._parts.append("**")
        elif tag in ("em", "i"):
            self._parts.append("*")
        elif tag == "a":
            href = attr.get("href", "")
            # Make relative links absolute
            if href.startswith("/"):
                href = CONFLUENCE_BASE + href
            self._link_href = href
            self._link_text_parts = []
        elif tag == "table":
            self._flush_inline()
            self._parts.append("\n\n")
        elif tag == "th":
            self._parts.append("| ")
        elif tag == "td":
            self._parts.append("| ")
        elif tag == "hr":
            self._flush_inline()
            self._parts.append("\n\n---\n\n")

    def handle_endtag(self, tag: str):
        tag = tag.lower()

        if self._skip_depth:
            self._skip_depth -= 1
            if self._tag_stack and self._tag_stack[-1] == tag:
                self._tag_stack.pop()
            return

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._parts.append("\n")
        elif tag == "ul":
            if self._list_stack:
                self._list_stack.pop()
            self._parts.append("\n")
        elif tag == "ol":
            if self._list_stack:
                self._list_stack.pop()
            if self._ol_counters:
                self._ol_counters.pop()
            self._parts.append("\n")
        elif tag == "pre":
            self._in_pre = False
            self._parts.append("\n```\n\n")
        elif tag == "code" and not self._in_pre:
            self._in_code = False
            self._parts.append("`")
        elif tag in ("strong", "b"):
            self._parts.append("**")
        elif tag in ("em", "i"):
            self._parts.append("*")
        elif tag == "a" and self._link_href is not None:
            text = "".join(self._link_text_parts).strip()
            href = self._link_href
            if text:
                self._parts.append(f"[{text}]({href})")
            else:
                self._parts.append(href)
            self._link_href = None
            self._link_text_parts = []
        elif tag == "tr":
            self._parts.append("|\n")

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        if self._link_href is not None:
            self._link_text_parts.append(data)
            return
        if self._in_pre:
            self._parts.append(data)
        else:
            self._parts.append(data)

    def _flush_inline(self):
        pass  # state is written directly to _parts

    def result(self) -> str:
        text = "".join(self._parts)
        # Collapse 3+ blank lines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def html_to_markdown(html: str) -> str:
    parser = _MarkdownConverter()
    parser.feed(html)
    return parser.result()


# ---------------------------------------------------------------------------
# Confluence API helpers
# ---------------------------------------------------------------------------

def _auth() -> HTTPBasicAuth:
    if not EMAIL or not API_KEY:
        sys.exit(
            "Error: set CONFLUENCE_EMAIL and API_KEY in "
            "IPPSAnalytics-Setup/.env before running this script."
        )
    return HTTPBasicAuth(EMAIL, API_KEY)


def search_page(project_num: str) -> dict | None:
    """Return the best-matching Confluence page for a project number."""
    cql = f'space = "{SPACE_KEY}" AND title ~ "{project_num}" AND type = page'
    r = requests.get(
        f"{CONFLUENCE_BASE}/rest/api/content/search",
        auth=_auth(),
        params={"cql": cql, "expand": "body.storage", "limit": 10},
        timeout=15,
    )
    r.raise_for_status()
    results = r.json().get("results", [])

    # Prefer a page whose title starts with the project number
    for page in results:
        if re.match(rf"^{project_num}[\s\-_]", page["title"]):
            return page
    # Fall back to first result that contains the number as a word
    for page in results:
        if re.search(rf"\b{project_num}\b", page["title"]):
            return page
    return None


def page_url(page: dict) -> str:
    page_id = page["id"]
    return f"{CONFLUENCE_BASE}/spaces/{SPACE_KEY}/pages/{page_id}"


# ---------------------------------------------------------------------------
# README builder
# ---------------------------------------------------------------------------

def build_readme(folder_name: str, page: dict) -> str:
    title = page["title"]
    url = page_url(page)
    body_html = page.get("body", {}).get("storage", {}).get("value", "")
    body_md = html_to_markdown(body_html)

    return f"# {title}\n\n> [View on Confluence]({url})\n\n{body_md}\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def fetch_confluence_context(project_num: str) -> str:
    """Fetch Confluence content for a project and return it as markdown text for use in prompts."""
    repo_root = Path(__file__).parent.parent
    folder = next(
        (d for d in repo_root.iterdir() if re.match(rf"^{project_num}-", d.name)),
        None,
    )
    folder_name = folder.name if folder else f"{project_num}-Unknown"

    # List files in the project folder
    file_list = ""
    if folder and folder.exists():
        files = sorted(f.name for f in folder.iterdir() if f.is_file())
        file_list = "\n".join(f"- {f}" for f in files)

    page = search_page(project_num)
    if not page:
        return (
            f"## Project: {folder_name}\n\n"
            f"No Confluence page found for project {project_num}.\n\n"
            f"### Files in repo\n{file_list or '(none)'}\n"
        )

    title = page["title"]
    url = page_url(page)
    body_html = page.get("body", {}).get("storage", {}).get("value", "")
    body_md = html_to_markdown(body_html)

    return (
        f"## Project folder: {folder_name}\n\n"
        f"### Confluence page: {title}\n"
        f"URL: {url}\n\n"
        f"{body_md}\n\n"
        f"### Files in repo\n{file_list or '(none)'}\n"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Sync Confluence pages to README.md files for each project."
    )
    parser.add_argument(
        "--project",
        metavar="NUM",
        help="Sync only this project number, e.g. 755",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output without writing any files",
    )
    parser.add_argument(
        "--fetch-only",
        metavar="NUM",
        help="Print Confluence content for one project to stdout (for use in prompts)",
    )
    args = parser.parse_args()

    if args.fetch_only:
        print(fetch_confluence_context(args.fetch_only))
        return

    repo_root = Path(__file__).parent.parent

    project_dirs: list[tuple[str, Path]] = []
    for d in sorted(repo_root.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        m = re.match(r"^(\d+)-", d.name)
        if not m:
            continue
        num = m.group(1)
        if args.project and num != args.project:
            continue
        project_dirs.append((num, d))

    if not project_dirs:
        sys.exit(f"No project folders found{f' matching {args.project}' if args.project else ''}.")

    found = skipped = written = 0

    for num, project_dir in project_dirs:
        label = project_dir.name
        print(f"[{num}] {label} ...", end=" ", flush=True)

        try:
            page = search_page(num)
        except requests.HTTPError as e:
            print(f"HTTP error: {e}")
            skipped += 1
            continue

        if not page:
            print("no Confluence page found — skipped")
            skipped += 1
            continue

        found += 1
        readme_content = build_readme(label, page)
        readme_path = project_dir / "README.md"

        if args.dry_run:
            print(f"DRY RUN → {readme_path.relative_to(repo_root)}")
            print("  " + readme_content[:200].replace("\n", "\n  "))
        else:
            readme_path.write_text(readme_content, encoding="utf-8")
            print(f"wrote README.md  ← {page['title']}")
            written += 1

    print(f"\nDone: {found} pages matched, {written} README{'s' if written != 1 else ''} written, {skipped} skipped.")


if __name__ == "__main__":
    main()
