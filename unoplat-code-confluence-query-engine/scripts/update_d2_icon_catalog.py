# ruff: noqa: INP001
"""Refresh URL-only D2 icon catalogs from https://icons.d2lang.com/.

This script stores metadata and hosted URLs only. It never downloads or vendors
SVG bytes. Run it from the query-engine package directory with:

    uv run python scripts/update_d2_icon_catalog.py
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import html
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

CATALOG_URL = "https://icons.d2lang.com/"
DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "unoplat_code_confluence_query_engine"
    / "skills"
    / "architecture-diagrams"
    / "icons"
)

ICON_PATTERN = re.compile(
    r"data-search=(?:\"(?P<quoted_label>[^\"]*)\"|(?P<bare_label>[^\s>]+))\s+"
    r"onclick='clickIcon\(\"(?P<encoded_path>[^\"]+)\"\)'"
)


@dataclass(frozen=True)
class Category:
    local_name: str
    hosted_prefix: str


CATEGORIES = (
    Category(local_name="development", hosted_prefix="dev"),
    Category(local_name="technology", hosted_prefix="tech"),
    Category(local_name="infrastructure", hosted_prefix="infra"),
)


def parse_icons(index_html: str, category: Category) -> list[dict[str, str]]:
    """Extract one category's labels and hosted URLs from the catalog page."""
    icons: list[dict[str, str]] = []
    expected_prefix = f"{category.hosted_prefix}/"

    for match in ICON_PATTERN.finditer(index_html):
        encoded_path = html.unescape(match.group("encoded_path"))
        hosted_path = urllib.parse.unquote(encoded_path)
        if not hosted_path.startswith(expected_prefix):
            continue

        raw_label = match.group("quoted_label") or match.group("bare_label") or ""
        label = html.unescape(raw_label)
        icons.append(
            {
                "name": Path(hosted_path).stem,
                "label": label,
                "hosted_path": hosted_path,
                "url": urllib.parse.urljoin(
                    CATALOG_URL,
                    urllib.parse.quote(hosted_path, safe="/"),
                ),
            }
        )

    icons.sort(key=lambda icon: (icon["name"].casefold(), icon["hosted_path"]))
    return icons


def write_catalogs(index_html: str, output_dir: Path) -> None:
    """Write deterministic JSON catalogs for all configured categories."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for category in CATEGORIES:
        icons = parse_icons(index_html, category)
        if not icons:
            raise RuntimeError(
                f"No icons found for hosted category {category.hosted_prefix!r}; "
                "the catalog HTML structure may have changed."
            )

        category_dir = output_dir / category.local_name
        category_dir.mkdir(parents=True, exist_ok=True)
        catalog = {
            "schema_version": 1,
            "source": CATALOG_URL,
            "storage_policy": "hosted-url-references-only",
            "requires_internet_to_render": True,
            "category": category.local_name,
            "hosted_prefix": category.hosted_prefix,
            "icon_count": len(icons),
            "icons": icons,
        }
        (category_dir / "catalog.json").write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"{category.local_name}: {len(icons)} URL references")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-file",
        type=Path,
        help="Read a previously downloaded catalog HTML file instead of the network.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Catalog output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    if args.source_file is not None:
        index_html = args.source_file.read_text(encoding="utf-8")
    else:
        request = urllib.request.Request(
            CATALOG_URL,
            headers={"User-Agent": "unoplat-d2-icon-catalog/1"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            index_html = response.read().decode("utf-8")

    write_catalogs(index_html, args.output_dir.resolve())


if __name__ == "__main__":
    main()
