"""Caching control commands."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Annotated

import typer

from openapi_diagram import CACHE_DIR
from openapi_diagram import OPENAPI_TO_PLANTUML_DEFAULT_VERSION
from openapi_diagram.openapi_to_plantuml import download_openapi_to_plantuml
from openapi_diagram.openapi_to_plantuml import get_openapi_to_plantuml_path

if TYPE_CHECKING:
    from pathlib import Path

cache_app = typer.Typer(no_args_is_help=True)


def _remove_cache_file(file_path: Path) -> None:
    """Remove cached file and pint the file name.

    Parameters
    ----------
    file_path : Path
        Path to the file that should be removed
    """
    file_path.unlink()
    print(f"Removed {file_path.name!r} from cache.")  # noqa: T201


@cache_app.command()
def show():
    """Show cached openapi-to-plantuml *.jar files."""
    for cached_file in CACHE_DIR.glob("*.jar"):
        print(cached_file.resolve().as_posix())  # noqa: T201
    raise typer.Exit(0)


@cache_app.command()
def remove(
    version: Annotated[
        str,
        typer.Option(
            help=(
                "Version to remove from cache. "
                "If 'all' is passed all files will be removed from cache."
            )
        ),
    ],
):
    """Remove files openapi-to-plantuml *.jar from caches."""
    if version == "all":
        for cached_file in CACHE_DIR.glob("*.jar"):
            _remove_cache_file(cached_file)
        raise typer.Exit(0)
    cached_file = get_openapi_to_plantuml_path(version)
    if cached_file.is_file() is False:
        msg = f"Nothing cached for version {version!r}."
        raise FileNotFoundError(msg)
    _remove_cache_file(cached_file)
    raise typer.Exit(0)


@cache_app.command()
def get(
    version: Annotated[
        str, typer.Option(help="Version to download.")
    ] = OPENAPI_TO_PLANTUML_DEFAULT_VERSION,
):
    """Download openapi-to-plantuml *.jar file into cache."""
    cached_file = get_openapi_to_plantuml_path(version)
    if cached_file.is_file() is True:
        print(f"openapi-to-plantuml version {version!r} is already in cache.")  # noqa: T201
        print(cached_file.resolve().as_posix())  # noqa: T201
        raise typer.Exit(0)
    print(f"Downloading openapi-to-plantuml version {version!r}.")  # noqa: T201
    cached_file = download_openapi_to_plantuml(version)
    print(f"Added openapi-to-plantuml version {version!r} to cache.")  # noqa: T201
    print(cached_file.resolve().as_posix())  # noqa: T201
    raise typer.Exit(0)
