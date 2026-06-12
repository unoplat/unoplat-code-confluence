from __future__ import annotations

import click

from unoplat_code_confluence_cli.agent_md_runtime import (
    parse_repository_git_url,
    start_agent_md_generate_update,
)
from unoplat_code_confluence_cli.app_runtime import (
    AppRuntimeError,
    destroy_app,
    ensure_app_running,
    run_app,
    stop_app,
    update_app,
)
from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.ingestion_runtime import (
    start_repository_ingestion,
    validate_repository_git_url,
)
from unoplat_code_confluence_cli.setup_runtime import open_setup_url


def progress(message: str) -> None:
    click.echo(message, err=True)


@click.group()
def main() -> None:
    """Use Unoplat Code Confluence from the command line."""


@main.group(name="service")
def service() -> None:
    """Manage the local Unoplat Code Confluence app service."""


@service.command(name="run")
def service_run() -> None:
    """Start the pinned Unoplat Code Confluence app release."""
    settings = CliSettings()
    try:
        result = run_app(settings, progress=progress)
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))


@service.command(name="update")
def service_update() -> None:
    """Upgrade the pinned app release to the latest app release."""
    settings = CliSettings()
    try:
        result = update_app(settings, progress=progress)
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))


@service.command(name="stop")
def service_stop() -> None:
    """Stop the local app Docker Compose stack without deleting volumes."""
    settings = CliSettings()
    try:
        result = stop_app(settings, progress=progress)
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))


@service.command(name="destroy")
def service_destroy() -> None:
    """Stop the local app Docker Compose stack and delete volumes."""
    settings = CliSettings()
    try:
        result = destroy_app(settings, progress=progress)
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))


@main.command(name="ingest")
@click.argument("repository_git_url")
def ingest(repository_git_url: str) -> None:
    """Start ingestion for a repository git remote URL."""
    settings = CliSettings()
    try:
        normalized_git_url = validate_repository_git_url(repository_git_url)
        if settings.auto_start:
            ensure_app_running(settings)
        result = start_repository_ingestion(
            settings,
            repository_git_url=normalized_git_url,
        )
    except AppRuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))


@main.command(name="agent-md")
@click.argument("repository_git_url")
def agent_md(repository_git_url: str) -> None:
    """Generate or update AGENTS.md artifacts for a repository git remote URL.

    The pull request is published automatically when generation completes.
    """
    settings = CliSettings()
    try:
        normalized_git_url = parse_repository_git_url(
            repository_git_url
        ).repository_git_url
        if settings.auto_start:
            ensure_app_running(settings)
        result = start_agent_md_generate_update(
            settings,
            repository_git_url=normalized_git_url,
        )
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
            path="/onboarding",
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
