"""Tests for `openapi_diagram.cli.commands.cache`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from openapi_diagram import OPENAPI_TO_PLANTUML_DEFAULT_VERSION
from openapi_diagram import cli
from tests import RUN_SLOW_TEST

if TYPE_CHECKING:
    from pathlib import Path


def test_cli_cache_show(cached_openapi_to_plantuml: Path):
    """Show the full path of the cached jar."""
    runner = CliRunner()
    result = runner.invoke(cli.app, ["cache", "show"])
    assert result.exit_code == 0, result.output
    assert cached_openapi_to_plantuml.as_posix() in result.output


def test_cli_cache_remove_single_version(empty_cache_dir: Path):
    """Remove only specified version."""
    to_be_removed = empty_cache_dir / "openapi-to-plantuml-0.0.0.jar"
    to_be_removed.touch()
    assert to_be_removed.is_file() is True

    to_be_kept = empty_cache_dir / "openapi-to-plantuml-0.0.1.jar"
    to_be_kept.touch()
    assert to_be_kept.is_file() is True

    runner = CliRunner()
    result = runner.invoke(cli.app, ["cache", "remove", "--version", "0.0.0"])

    assert result.exit_code == 0, result.output
    assert to_be_removed.is_file() is False
    assert "Removed 'openapi-to-plantuml-0.0.0.jar' from cache." in result.output

    assert to_be_kept.is_file() is True
    assert "Removed 'openapi-to-plantuml-0.0.1.jar' from cache." not in result.output


def test_cli_cache_remove_all(empty_cache_dir: Path):
    """All cached versions are removed."""
    to_be_removed = empty_cache_dir / "openapi-to-plantuml-0.0.0.jar"
    to_be_removed.touch()
    assert to_be_removed.is_file() is True

    to_be_kept = empty_cache_dir / "openapi-to-plantuml-0.0.1.jar"
    to_be_kept.touch()
    assert to_be_kept.is_file() is True

    runner = CliRunner()
    result = runner.invoke(cli.app, ["cache", "remove", "--version", "all"])

    assert result.exit_code == 0, result.output
    assert to_be_removed.is_file() is False
    assert "Removed 'openapi-to-plantuml-0.0.0.jar' from cache." in result.output

    assert to_be_kept.is_file() is False
    assert "Removed 'openapi-to-plantuml-0.0.1.jar' from cache." in result.output


@pytest.mark.usefixtures("empty_cache_dir")
def test_cli_cache_remove_not_found():
    """Show error when no cache files exists for the specified version."""
    runner = CliRunner()
    result = runner.invoke(cli.app, ["cache", "remove", "--version", "0.0.0"])

    assert result.exit_code == 1, result.output
    assert "Nothing cached for version '0.0.0'." in str(result.exc_info)


def test_cli_cache_get_cache_hit(cached_openapi_to_plantuml: Path):
    """Output for cache hit."""
    runner = CliRunner()
    result = runner.invoke(
        cli.app, ["cache", "get", "--version", OPENAPI_TO_PLANTUML_DEFAULT_VERSION]
    )
    assert result.exit_code == 0, result.output
    assert (
        f"openapi-to-plantuml version '{OPENAPI_TO_PLANTUML_DEFAULT_VERSION}' is already in cache."
        in result.output
    )
    assert cached_openapi_to_plantuml.as_posix() in result.output


@pytest.mark.skipif(
    RUN_SLOW_TEST,
    reason="Since this is an upstream dependency there is no need to check it in all CI runs.",
)
def test_cli_cache_get_cache_miss(empty_cache_dir: Path):
    """Default version is downloaded to cache."""
    cached_openapi_to_plantuml = (
        empty_cache_dir / f"openapi-to-plantuml-{OPENAPI_TO_PLANTUML_DEFAULT_VERSION}.jar"
    )
    runner = CliRunner()
    result = runner.invoke(cli.app, ["cache", "get"])
    assert result.exit_code == 0, result.output
    assert (
        f"Downloading openapi-to-plantuml version '{OPENAPI_TO_PLANTUML_DEFAULT_VERSION}'"
        in result.output
    )
    assert (
        f"Added openapi-to-plantuml version '{OPENAPI_TO_PLANTUML_DEFAULT_VERSION}' to cache."
        in result.output
    )
    assert cached_openapi_to_plantuml.is_file() is True
    assert cached_openapi_to_plantuml.as_posix() in result.output
