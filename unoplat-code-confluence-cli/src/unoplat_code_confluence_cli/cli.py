from __future__ import annotations

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
    click.echo(result.model_dump_json(indent=2))


@main.command(name="update")
def update() -> None:
    """Upgrade the pinned app release to the latest app release."""
    settings = CliSettings()
    try:
        result = update_app(settings, progress=progress)
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))
