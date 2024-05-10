"""Tests for `openapi_diagram.cli.commands.create`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typer.testing import CliRunner

from openapi_diagram import cli
from tests import TEST_DATA

if TYPE_CHECKING:
    from pathlib import Path


def test_cli_create(tmp_path: Path):
    """Test the create command works."""
    runner = CliRunner()
    openapi_spec = TEST_DATA / "petstore-3-0.json"
    output_path = tmp_path / "petstore.puml"
    result = runner.invoke(
        cli.app,
        [
            "create",
            "--openapi-spec",
            openapi_spec.as_posix(),
            "--output-path",
            output_path.as_posix(),
            "--mode",
            "single",
            "--diagram-format",
            "puml",
        ],
    )
    assert result.exit_code == 0, result.output
    assert output_path.is_file() is True
    assert output_path.read_text().rstrip() == (TEST_DATA / "petstore.puml").read_text().rstrip()
