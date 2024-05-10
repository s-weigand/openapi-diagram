"""Tests for `openapi_diagram.cli.commands.fetch`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typer.testing import CliRunner

from openapi_diagram import cli
from tests import TEST_DATA

if TYPE_CHECKING:
    from pathlib import Path

    from fastapi.testclient import TestClient


def test_cli_fetch_single_file(tmp_path: Path, app_client: TestClient):
    """Test fetching a single file from server."""
    runner = CliRunner()
    base_url = app_client.base_url
    openapi_spec = TEST_DATA / "petstore-3-0.json"
    output_path = tmp_path / "petstore.puml"
    result = runner.invoke(
        cli.app,
        [
            "fetch",
            "--openapi-spec",
            openapi_spec.as_posix(),
            "--output-path",
            output_path.as_posix(),
            "--mode",
            "single",
            "--diagram-format",
            "puml",
            "--base-url",
            str(base_url),
        ],
    )
    assert result.exit_code == 0, result.output
    assert output_path.is_file() is True
    assert output_path.read_text().rstrip() == (TEST_DATA / "petstore.puml").read_text().rstrip()


def test_cli_fetch_multiple_files(tmp_path: Path, app_client: TestClient):
    """Test fetching a multiple files from server."""
    runner = CliRunner()
    base_url = app_client.base_url
    openapi_spec = TEST_DATA / "petstore-3-0.json"
    output_path = tmp_path
    result = runner.invoke(
        cli.app,
        [
            "fetch",
            "--openapi-spec",
            openapi_spec.as_posix(),
            "--output-path",
            output_path.as_posix(),
            "--mode",
            "split",
            "--diagram-format",
            "puml",
            "--base-url",
            str(base_url),
        ],
    )
    assert result.exit_code == 0, result.output
    assert len(list(output_path.glob("*.puml"))) == 19
