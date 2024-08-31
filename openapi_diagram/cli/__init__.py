"""Console script for openapi_diagram."""

from __future__ import annotations

import typer
from rich import print

from openapi_diagram import __version__
from openapi_diagram.cli.commands.cache import cache_app
from openapi_diagram.cli.commands.create import create
from openapi_diagram.cli.commands.fetch import fetch
from openapi_diagram.cli.commands.serve import create_serve_callback


def version_callback(value: bool):
    """Implement showing version to show version."""
    if value:
        print(
            "[bold green]Openapi-Diagram[/bold green] Version: "
            f"[dark_orange]{__version__}[/dark_orange]"
        )
        raise typer.Exit(0)


app = typer.Typer(name="openapi-diagram", rich_markup_mode="rich", no_args_is_help=True)


@app.callback()
def show_version(
    _ctx: typer.Context,
    _version: bool = typer.Option(None, "--version", "-V", callback=version_callback),
):
    """Show version when using `--version` flag."""


app.add_typer(cache_app, name="cache")


app.command()(create)

app.command(name="serve")(create_serve_callback())
app.command()(fetch)


if __name__ == "__main__":
    app()
