from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import click

from unoplat_code_confluence_cli.app_runtime import AppRuntimeError, run_app, update_app
from unoplat_code_confluence_cli.config import CliSettings


def progress(message: str) -> None:
    click.echo(message, err=True)


@click.group()
def main() -> None:
    """Use Unoplat Code Confluence from the command line."""


@main.command(name="run")
def run() -> None:
    """Start the pinned Unoplat Code Confluence app release."""
    settings = CliSettings()
    try:
        result = run_app(settings, progress=progress)
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(to_jsonable(asdict(result)), indent=2, sort_keys=True))


@main.command(name="update")
def update() -> None:
    """Upgrade the pinned app release to the latest app release."""
    settings = CliSettings()
    try:
        result = update_app(settings, progress=progress)
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(to_jsonable(asdict(result)), indent=2, sort_keys=True))


def to_jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    return value
