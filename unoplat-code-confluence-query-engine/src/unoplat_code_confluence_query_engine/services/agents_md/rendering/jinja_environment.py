"""Shared Jinja2 environment helpers for deterministic managed markdown rendering."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


def build_markdown_jinja_environment(template_dir: Path) -> Environment:
    """Build a deterministic Jinja2 environment for markdown templates."""
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
