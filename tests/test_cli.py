#!/usr/bin/env python

"""Tests for `openapi_diagram` package."""

from __future__ import annotations

import re

from typer.testing import CliRunner

from openapi_diagram import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.app)
    assert result.exit_code == 0
    assert "openapi_diagram.cli.main" in result.output
    help_result = runner.invoke(cli.app, ["--help"])
    assert help_result.exit_code == 0
    assert re.search(r"--help\s+Show this message and exit.", help_result.output)
