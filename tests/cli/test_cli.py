"""Tests for `openapi_diagram.cli` main app."""

from __future__ import annotations

import re

from typer.testing import CliRunner

from openapi_diagram import __version__
from openapi_diagram import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.app)
    assert result.exit_code == 0
    assert "openapi-diagram [OPTIONS] COMMAND [ARGS]..." in result.output
    help_result = runner.invoke(cli.app, ["--help"])
    assert help_result.exit_code == 0
    assert re.search(
        r"--help\s+Show this message and exit.", help_result.output
    ), help_result.output


def test_command_line_interface_version():
    """Version flag shows correct version."""
    runner = CliRunner()
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"Openapi-Diagram Version: {__version__}\n"
