"""Tests for ``openapi_diagram.dependencies``."""

from __future__ import annotations

from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING
from typing import get_args
from unittest.mock import MagicMock

import httpx
import pytest

from openapi_diagram import OPENAPI_TO_PLANTUML_DEFAULT_VERSION
from openapi_diagram.openapi_to_plantuml import OPENAPI_TO_PLANTUML_MAVEN_URL
from openapi_diagram.openapi_to_plantuml import DownloadVerificationError
from openapi_diagram.openapi_to_plantuml import MissingDependecyWarning
from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlFormats
from openapi_diagram.openapi_to_plantuml import _find_java_executable
from openapi_diagram.openapi_to_plantuml import _get_latest_openapi_to_plantuml_version
from openapi_diagram.openapi_to_plantuml import _get_openapi_to_plantuml_download_url
from openapi_diagram.openapi_to_plantuml import download_openapi_to_plantuml
from openapi_diagram.openapi_to_plantuml import get_openapi_to_plantuml_path
from openapi_diagram.openapi_to_plantuml import run_openapi_to_plantuml
from tests import RUN_SLOW_TEST
from tests import TEST_DATA

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


EXPECTED_DOWNLOAD_URL = (
    "https://repo1.maven.org/maven2/com/github/davidmoten/openapi-to-plantuml/0.1.28/"
    "openapi-to-plantuml-0.1.28-jar-with-dependencies.jar"
)


def test_get_latest_openapi_to_plantuml_version(httpx_mock: HTTPXMock):
    """Currently the latest."""
    httpx_mock.add_response(
        url=f"{OPENAPI_TO_PLANTUML_MAVEN_URL}/maven-metadata.xml",
        content=(TEST_DATA / "maven-metadata.xml").read_bytes(),
    )
    assert _get_latest_openapi_to_plantuml_version() == "0.1.28"


def test_get_latest_openapi_to_plantuml_version_not_found(httpx_mock: HTTPXMock):
    """Currently the latest."""
    httpx_mock.add_response(
        url=f"{OPENAPI_TO_PLANTUML_MAVEN_URL}/maven-metadata.xml",
        content=b"<bad-file>\n</bad-file>",
    )
    with pytest.raises(RuntimeError) as execinfo:
        _get_latest_openapi_to_plantuml_version()
    assert (
        str(execinfo.value)
        == "Could not find openapi-to-plantuml version in 'maven-metadata.xml':\n"
        "<bad-file>\n"
        "</bad-file>"
    )


def test_get_openapi_to_plantuml_download_link(httpx_mock: HTTPXMock):
    """Got correct download link."""
    httpx_mock.add_response(
        url=f"{OPENAPI_TO_PLANTUML_MAVEN_URL}/0.1.28",
        content=(TEST_DATA / "0.1.28-maven-release-page.html").read_bytes(),
    )
    assert _get_openapi_to_plantuml_download_url("0.1.28") == EXPECTED_DOWNLOAD_URL


def test_get_openapi_to_plantuml_download_link_not_found(httpx_mock: HTTPXMock):
    """Raise runtime error if download link can not be found."""
    httpx_mock.add_response(
        url=f"{OPENAPI_TO_PLANTUML_MAVEN_URL}/0.1.28",
        content=b"<html>\n</html>",
    )
    with pytest.raises(RuntimeError) as execinfo:
        _get_openapi_to_plantuml_download_url("0.1.28")
    assert (
        str(execinfo.value) == "Could not find openapi-to-plantuml download link in:\n"
        "<html>\n"
        "</html>"
    )


def test_get_openapi_to_plantuml_path(empty_cache_dir: Path):
    """This mainly tests the mock."""
    docstring = get_openapi_to_plantuml_path.__doc__
    assert docstring is not None
    assert OPENAPI_TO_PLANTUML_DEFAULT_VERSION in docstring
    jar_path = get_openapi_to_plantuml_path("0.0.0")
    assert jar_path == empty_cache_dir / "openapi-to-plantuml-0.0.0.jar"


@pytest.mark.skipif(
    RUN_SLOW_TEST,
    reason="Since this tests if the download works there is no need to check it in all CI runs.",
)
@pytest.mark.usefixtures("empty_cache_dir")
def test_download_openapi_to_plantuml():
    """Download creates the expected file."""
    jar_path = get_openapi_to_plantuml_path()

    assert jar_path.is_file() is False

    download_openapi_to_plantuml()

    assert jar_path.is_file() is True


@pytest.mark.usefixtures("empty_cache_dir")
def test_download_openapi_to_plantuml_verification_error(httpx_mock: HTTPXMock):
    """Raise ``DownloadVerificationError`` if hash of download and expected hash do not match."""
    httpx_mock.add_response(
        url=f"{OPENAPI_TO_PLANTUML_MAVEN_URL}/0.1.28",
        content=(TEST_DATA / "0.1.28-maven-release-page.html").read_bytes(),
    )
    httpx_mock.add_response(url=f"{EXPECTED_DOWNLOAD_URL}", content=b"bad_file_content")
    httpx_mock.add_response(url=f"{EXPECTED_DOWNLOAD_URL}.md5", content=b"bad_md5")
    with pytest.raises(DownloadVerificationError) as execinfo:
        download_openapi_to_plantuml("0.1.28")
    assert str(execinfo.value) == "Downloaded openapi-to-plantuml jar has invalid hash."


def test_download_openapi_to_plantuml_use_cached(monkeypatch: pytest.MonkeyPatch):
    """Download early exits and does not call actual download functionality."""
    docstring = download_openapi_to_plantuml.__doc__
    assert docstring is not None
    assert OPENAPI_TO_PLANTUML_DEFAULT_VERSION in docstring
    with monkeypatch.context() as m:
        mock = MagicMock()
        m.setattr(httpx, "get", mock)

        download_openapi_to_plantuml()

        mock.assert_not_called()


def test__find_java_executable_java_home(monkeypatch: pytest.MonkeyPatch):
    """Get java from JAVA_HOME env var."""
    with monkeypatch.context() as m:
        m.setenv("JAVA_HOME", "/usr/local/java")
        assert _find_java_executable() == Path("/usr/local/java/bin/java")


def test__find_java_executable_path(monkeypatch: pytest.MonkeyPatch):
    """Get java from PATH env var."""
    with monkeypatch.context() as m:
        m.delenv("JAVA_HOME")
        java_path = which("java")
        assert java_path is not None
        assert _find_java_executable() == Path(java_path)


@pytest.mark.parametrize(
    "spec_file", ["petstore-3-0.json", "petstore-3-0.yaml", "petstore-3-1.yaml"]
)
def test_run_openapi_to_plantuml(tmp_path: Path, spec_file: str):
    """Generated PUML files are equivalent for JSON and YAML as well 3.1 specs."""
    docstring = run_openapi_to_plantuml.__doc__
    assert docstring is not None
    assert OPENAPI_TO_PLANTUML_DEFAULT_VERSION in docstring
    openapi_spec = TEST_DATA / spec_file
    output = tmp_path / "result.puml"
    result = run_openapi_to_plantuml(openapi_spec, output, "single", "puml")
    assert len(result) == 1
    assert result[0] == output
    assert output.read_text().rstrip() == (TEST_DATA / "petstore.puml").read_text().rstrip()


def test_run_openapi_to_plantuml_split(tmp_path: Path):
    """Using `split` generation creates multiple files."""
    openapi_spec = TEST_DATA / "petstore-3-0.json"
    output = tmp_path
    result = run_openapi_to_plantuml(openapi_spec, output, "split", "svg")
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
    output = tmp_path / "result"
    result = run_openapi_to_plantuml(openapi_spec, output, "split", output_format)
    assert len(result) == 19
    assert (output / f"deleteOrder.{output_format}") in result


@pytest.mark.usefixtures("_mock_empty_path")
def test_run_openapi_to_plantuml_java_not_installed(tmp_path: Path):
    """Raise Runtime error if java can not be found on the path."""
    with pytest.raises(RuntimeError) as exceinfo, pytest.warns(
        MissingDependecyWarning,
        match="Graphviz installation not found, some output formats might not be available.",
    ):
        run_openapi_to_plantuml(tmp_path, tmp_path, "single", "svg")
    assert str(exceinfo.value) == (
        "Can not run openapi-to-plantuml without java installed."
        "Couldn't find the 'JAVA_HOME' environment variable or java on the PATH."
    )
