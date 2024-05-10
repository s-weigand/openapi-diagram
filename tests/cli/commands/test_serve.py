"""Tests for `openapi_diagram.cli.commands.serve`."""

from __future__ import annotations

import re

from typer.testing import CliRunner

from openapi_diagram import cli


def test_cli_serve():
    """Same help as ``fastapi-cli run``."""
    runner = CliRunner()
    help_result = runner.invoke(cli.app, ["serve", "--help"])
    assert help_result.exit_code == 0
    assert re.search(
        r"--host\s+TEXT\s+The host to serve on. For local development in localhost use",
        help_result.output,
    ), help_result.output
