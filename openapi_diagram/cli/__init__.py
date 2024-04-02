"""Console script for openapi_diagram."""

from __future__ import annotations

import typer

from openapi_diagram.cli.commands.cache import cache_app
from openapi_diagram.cli.commands.create import create

app = typer.Typer(name="openapi-diagram", no_args_is_help=True)

app.add_typer(cache_app, name="cache")


app.command()(create)


if __name__ == "__main__":
    app()
