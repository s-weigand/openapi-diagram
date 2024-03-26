"""Caching control commands."""

from __future__ import annotations

import typer

from openapi_diagram import CACHE_DIR
from openapi_diagram.openapi_to_plantuml import download_openapi_to_plantuml
from openapi_diagram.openapi_to_plantuml import get_openapi_to_plantuml_path

cache_app = typer.Typer()


@cache_app.command()
def show(
    full_path: bool = typer.Option(
        default=False, help="Where to show the full path to cached files or only the file name."
    ),
):
    """Show cached files."""
    for cached_file in CACHE_DIR.glob("*"):
        if full_path is False:
            print(cached_file.name)  # noqa: T201
        else:
            print(cached_file.resolve().as_posix())  # noqa: T201
    raise typer.Exit(0)


@cache_app.command()
def remove(
    version: str = typer.Argument(
        help="Version to remove from cache. If 'all' is passed all version are removed."
    ),
):
    """Remove files from caches."""
    if version == "all":
        for cached_file in CACHE_DIR.glob("*"):
            cached_file.unlink()
        raise typer.Exit(0)
    cached_file = get_openapi_to_plantuml_path(version)
    if cached_file.is_file() is False:
        msg = f"Nothing cached for version: {version!r}"
        raise FileNotFoundError(msg)
    cached_file.unlink()
    raise typer.Exit(0)


@cache_app.command()
def get(version: str = typer.Argument(default="0.1.28", help="Version to download.")):
    """Download openapi-to-plantuml into cache."""
    download_openapi_to_plantuml(version)
    raise typer.Exit(0)
