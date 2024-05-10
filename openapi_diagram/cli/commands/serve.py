"""Command to start REST server."""

from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Callable

from fastapi_cli.cli import app as fastapi_cli_app

from openapi_diagram.server import app as rest_app


def create_serve_callback() -> Callable:
    """Extract ``run`` command from ``fastapi-cli`` and set app path."""
    for command_info in fastapi_cli_app.registered_commands:
        callback = command_info.callback
        if callback.__name__ == "run":
            run = callback
            break
    else:  # pragma: no cover
        msg = "Could not extract run callback from fastapi-cli."
        raise RuntimeError(msg)
    fastapi_cli_run = partial(run, Path(rest_app.__file__))
    run.__annotations__.pop("path", None)
    fastapi_cli_run.__annotations__ = run.__annotations__
    fastapi_cli_run.__doc__ = "Run [green]openapi-diagram[/green] REST server."
    return fastapi_cli_run
