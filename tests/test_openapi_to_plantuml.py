"""Tests for ``openapi_diagram.dependencies``."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from typing import get_args
from unittest.mock import MagicMock

import httpx
import pytest

from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlFormats
from openapi_diagram.openapi_to_plantuml import _get_latest_openapi_to_plantuml_version
from openapi_diagram.openapi_to_plantuml import _get_openapi_to_plantuml_download_url
from openapi_diagram.openapi_to_plantuml import download_openapi_to_plantuml
from openapi_diagram.openapi_to_plantuml import get_openapi_to_plantuml_paths
from openapi_diagram.openapi_to_plantuml import is_graphviz_installed
from openapi_diagram.openapi_to_plantuml import is_java_installed
from openapi_diagram.openapi_to_plantuml import run_openapi_to_plantuml
from tests import RUN_SLOW_TEST
from tests import TEST_DATA

if TYPE_CHECKING:
    from pathlib import Path


def test_is_graphviz_installed():
    """Grapthviz is installed."""
    assert is_graphviz_installed() is True


@pytest.mark.usefixtures("mock_empty_path")
def test_is_graphviz_installed_fail():
    """Grapthviz is not installed."""
    assert is_graphviz_installed() is False


def test_is_java_installed():
    """Java is installed."""
    assert is_java_installed() is True


@pytest.mark.usefixtures("mock_empty_path")
def test_is_java_installed_fail():
    """Java is not installed."""
    assert is_java_installed() is False


def test_get_latest_openapi_to_plantuml_version(monkeypatch: pytest.MonkeyPatch):
    """Currently the latest."""
    with monkeypatch.context() as m:
        m.setattr(httpx.Response, "content", (TEST_DATA / "maven-metadata.xml").read_bytes())
        assert _get_latest_openapi_to_plantuml_version() == "0.1.28"


def test_get_latest_openapi_to_plantuml_version_not_found(monkeypatch: pytest.MonkeyPatch):
    """Currently the latest."""
    with monkeypatch.context() as m:
        m.setattr(httpx.Response, "content", b"<bad-file>\n</bad-file>")
        with pytest.raises(RuntimeError) as execinfo:
            _get_latest_openapi_to_plantuml_version()
        assert (
            str(execinfo.value)
            == "Could not find openapi-to-plantuml version in 'maven-metadata.xml':\n"
            "<bad-file>\n"
            "</bad-file>"
        )


def test_get_openapi_to_plantuml_download_link(monkeypatch: pytest.MonkeyPatch):
    """Got correct download link."""
    with monkeypatch.context() as m:
        m.setattr(
            httpx.Response, "content", (TEST_DATA / "0.1.28-maven-release-page.html").read_bytes()
        )
    assert (
        _get_openapi_to_plantuml_download_url("0.1.28")
        == "https://repo1.maven.org/maven2/com/github/davidmoten/openapi-to-plantuml/0.1.28/openapi-to-plantuml-0.1.28-jar-with-dependencies.jar"
    )


def test_get_openapi_to_plantuml_paths(mock_cache_dir: Path):
    """This mainly tests the mock."""
    jar_path, version_path = get_openapi_to_plantuml_paths()
    assert jar_path == mock_cache_dir / "openapi-to-plantuml.jar"
    assert version_path == mock_cache_dir / "openapi-to-plantuml.version"


@pytest.mark.skipif(
    RUN_SLOW_TEST,
    reason="Since this tests if the download works there is no need to check it in all CI runs.",
)
@pytest.mark.usefixtures("mock_cache_dir")
def test_download_openapi_to_plantuml():
    """Download creates the expected files."""
    jar_path, version_path = get_openapi_to_plantuml_paths()

    assert jar_path.is_file() is False
    assert version_path.is_file() is False

    download_openapi_to_plantuml()

    assert jar_path.is_file() is True
    assert version_path.is_file() is True


def test_download_openapi_to_plantuml_use_cached(monkeypatch: pytest.MonkeyPatch):
    """Download early exits and does not call actual download functionality."""
    with monkeypatch.context() as m:
        mock = MagicMock()
        m.setattr(httpx, "get", mock)

        download_openapi_to_plantuml()

        mock.assert_not_called()


@pytest.mark.parametrize(
    "spec_file", ["petstore-3-0.json", "petstore-3-0.yaml", "petstore-3-1.yaml"]
)
def test_run_openapi_to_plantuml(tmp_path: Path, spec_file: str):
    """Generated SVG files are equivalent for JSON and YAML as well 3.1 specs."""
    openapi_spec = TEST_DATA / spec_file
    output = tmp_path / "result.svg"
    result = run_openapi_to_plantuml(openapi_spec, output, "single", "SVG")
    assert len(result) == 1
    assert result[0] == output
    assert output.read_text() == (TEST_DATA / "petstore.svg").read_text()


def test_run_openapi_to_plantuml_split(tmp_path: Path):
    """Using `split` generation creates multiple files."""
    openapi_spec = TEST_DATA / "petstore-3-0.json"
    output = tmp_path
    result = run_openapi_to_plantuml(openapi_spec, output, "split", "SVG")
    assert len(result) == 19


@pytest.mark.skipif(
    RUN_SLOW_TEST,
    reason="Since this is an upstream dependency there is no need to check it in all CI runs.",
)
@pytest.mark.parametrize("output_format", get_args(OpenapiToPlantumlFormats))
def test_run_openapi_to_plantuml_output_format(
    tmp_path: Path, output_format: OpenapiToPlantumlFormats
):
    """Test all format supported by `openapi-to-plantuml`."""
    openapi_spec = TEST_DATA / "petstore-3-0.json"
    output = tmp_path / "result.svg"
    result = run_openapi_to_plantuml(openapi_spec, output, "single", output_format)
    assert len(result) == 1
    assert result[0] == output
