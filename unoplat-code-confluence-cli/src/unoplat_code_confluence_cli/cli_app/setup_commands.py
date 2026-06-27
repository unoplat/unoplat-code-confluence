from __future__ import annotations

import click

from unoplat_code_confluence_cli.cli_app.context import CliServices
from unoplat_code_confluence_cli.cli_app.output import json_command, progress
from unoplat_code_confluence_cli.domain.results import SetupOpenResult


@click.group(name="setup")
def setup_group() -> None:
    """Open setup pages in the Unoplat Code Confluence app."""



@setup_group.command(name="token-repo-provider")
@click.pass_obj
@json_command
def setup_token_repo_provider(services: CliServices) -> SetupOpenResult:
    """Open the GitHub repository-provider setup page."""
    return services.setup.open_setup_url(
        setup_target="token-repo-provider",
        path="/onboarding",
        progress=progress,
    )


@setup_group.command(name="model-provider")
@click.pass_obj
@json_command
def setup_model_provider(services: CliServices) -> SetupOpenResult:
    """Open the model-provider setup page."""
    return services.setup.open_setup_url(
        setup_target="model-provider",
        path="/settings/model-providers",
        progress=progress,
    )
