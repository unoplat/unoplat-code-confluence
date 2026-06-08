from __future__ import annotations

import click

from unoplat_code_confluence_cli.app_runtime import (
    AppRuntimeError,
    ensure_app_running,
    run_app,
    update_app,
)
from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.setup_runtime import open_setup_url


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


@main.group(name="setup")
def setup() -> None:
    """Open setup pages in the Unoplat Code Confluence app."""


@setup.command(name="token-repo-provider")
def setup_token_repo_provider() -> None:
    """Open the GitHub repository-provider setup page."""
    settings = CliSettings()
    try:
        ensure_app_running(settings)
        result = open_setup_url(
            settings,
            setup_target="token-repo-provider",
            path="/onboarding/github",
        )
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))


@setup.command(name="model-provider")
def setup_model_provider() -> None:
    """Open the model-provider setup page."""
    settings = CliSettings()
    try:
        ensure_app_running(settings)
        result = open_setup_url(
            settings,
            setup_target="model-provider",
            path="/settings/model-providers",
        )
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))
