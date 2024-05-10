"""Console script for openapi_diagram."""

from __future__ import annotations

import typer

from openapi_diagram.cli.commands.cache import cache_app
from openapi_diagram.cli.commands.create import create
from openapi_diagram.cli.commands.fetch import fetch
from openapi_diagram.cli.commands.serve import create_serve_callback

app = typer.Typer(name="openapi-diagram", rich_markup_mode="rich", no_args_is_help=True)

app.add_typer(cache_app, name="cache")


app.command()(create)

app.command(name="serve")(create_serve_callback())
app.command()(fetch)


if __name__ == "__main__":
    app()
