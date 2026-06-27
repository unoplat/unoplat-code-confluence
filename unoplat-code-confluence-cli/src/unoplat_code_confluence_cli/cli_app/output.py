from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

import click
from pydantic import BaseModel

from unoplat_code_confluence_cli.errors import CliError

P = ParamSpec("P")
R = TypeVar("R", bound=BaseModel)


def progress(message: str) -> None:
    click.echo(message, err=True)


def json_command(function: Callable[P, R]) -> Callable[P, None]:
    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            result = function(*args, **kwargs)
        except CliError as exc:
            raise click.ClickException(str(exc)) from exc
        click.echo(result.model_dump_json(indent=2))

    return wrapper
