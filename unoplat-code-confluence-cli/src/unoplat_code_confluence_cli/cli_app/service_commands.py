from __future__ import annotations

import click

from unoplat_code_confluence_cli.cli_app.context import CliServices
from unoplat_code_confluence_cli.cli_app.output import json_command, progress
from unoplat_code_confluence_cli.domain.results import (
    AppDownResult,
    AppRunResult,
    AppUpdateResult,
    SetupStatusResult,
)


@click.group(name="service")
def service_group() -> None:
    """Manage the local Unoplat Code Confluence app service."""


@service_group.command(name="run")
@click.pass_obj
@json_command
def service_run(services: CliServices) -> AppRunResult:
    """Start the pinned Unoplat Code Confluence app release."""
    return services.app.run(progress=progress)


@service_group.command(name="status")
@click.option(
    "--repository-provider-key",
    default=None,
    help="Repository provider key to verify. Defaults to configured default provider.",
)
@click.pass_obj
@json_command
def service_status(
    services: CliServices,
    repository_provider_key: str | None,
) -> SetupStatusResult:
    """Verify repository-provider and model-provider setup state."""
    return services.setup.get_status(
        repository_provider_key=repository_provider_key,
        progress=progress,
    )


@service_group.command(name="update")
@click.pass_obj
@json_command
def service_update(services: CliServices) -> AppUpdateResult:
    """Upgrade the pinned app release to the latest app release."""
    return services.app.update(progress=progress)


@service_group.command(name="stop")
@click.pass_obj
@json_command
def service_stop(services: CliServices) -> AppDownResult:
    """Stop the local app Docker Compose stack without deleting volumes."""
    return services.app.stop(progress=progress)


@service_group.command(name="destroy")
@click.pass_obj
@json_command
def service_destroy(services: CliServices) -> AppDownResult:
    """Stop the local app Docker Compose stack and delete volumes."""
    return services.app.destroy(progress=progress)
