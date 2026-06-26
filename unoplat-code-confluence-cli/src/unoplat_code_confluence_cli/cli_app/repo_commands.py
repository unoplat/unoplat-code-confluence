from __future__ import annotations

import click

from unoplat_code_confluence_cli.cli_app.context import CliServices
from unoplat_code_confluence_cli.cli_app.output import json_command, progress
from unoplat_code_confluence_cli.domain.results import RepositoryAddResult, RepositoryRefreshResult


@click.group(name="repo")
def repo_group() -> None:
    """Manage tracked repositories."""


@repo_group.command(name="add")
@click.argument("repository_git_url")
@click.pass_obj
@json_command
def repo_add(services: CliServices, repository_git_url: str) -> RepositoryAddResult:
    """Add a repository without running ingestion."""
    return services.repository.add_repository(
        repository_git_url=repository_git_url,
        progress=progress,
    )


@click.command(name="add-repository")
@click.argument("repository_git_url")
@click.pass_obj
@json_command
def add_repository_command(
    services: CliServices,
    repository_git_url: str,
) -> RepositoryAddResult:
    """Add a repository without running ingestion."""
    return services.repository.add_repository(
        repository_git_url=repository_git_url,
        progress=progress,
    )


@click.command(name="agent-md")
@click.argument("repository_git_url")
@click.pass_obj
@json_command
def agent_md(
    services: CliServices,
    repository_git_url: str,
) -> RepositoryRefreshResult:
    """Generate or update AGENTS.md artifacts for a repository git remote URL.

    The pull request is published automatically when generation completes.
    """
    return services.repository.start_agent_md_generate_update(
        repository_git_url=repository_git_url,
        progress=progress,
    )
