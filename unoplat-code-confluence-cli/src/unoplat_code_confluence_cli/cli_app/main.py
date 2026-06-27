from __future__ import annotations

import click

from unoplat_code_confluence_cli.cli_app.context import build_services
from unoplat_code_confluence_cli.cli_app.repo_commands import (
    add_repository_command,
    agent_md,
    repo_group,
)
from unoplat_code_confluence_cli.cli_app.service_commands import service_group
from unoplat_code_confluence_cli.cli_app.setup_commands import setup_group


@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    """Use Unoplat Code Confluence from the command line."""
    ctx.obj = build_services()


def register_commands(root: click.Group) -> None:
    root.add_command(service_group)
    root.add_command(repo_group)
    root.add_command(add_repository_command)
    root.add_command(agent_md)
    root.add_command(setup_group)


register_commands(main)
