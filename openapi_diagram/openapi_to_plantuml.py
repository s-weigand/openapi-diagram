"""Module to check and fetch openapi_to_plantuml."""

from __future__ import annotations

import subprocess
from hashlib import md5
from shutil import which
from typing import TYPE_CHECKING
from typing import Literal
from typing import NamedTuple
from typing import TypeAlias
from typing import cast

import httpx
from bs4 import BeautifulSoup
from pydantic import TypeAdapter

from openapi_diagram import CACHE_DIR
from openapi_diagram.utils import openapi_3_dot_1_compat

if TYPE_CHECKING:
    from pathlib import Path

OPENAPI_TO_PLANTUML_MAVEN_URL = (
    "https://repo1.maven.org/maven2/com/github/davidmoten/openapi-to-plantuml"
)


OpenapiToPlantumlModes: TypeAlias = Literal["single", "split"]
# Commented out formats are format that are technically supported by openapi-to-plantuml
# But tests crash in the dev container
# Ref. https://github.com/davidmoten/openapi-to-plantuml/blob/f00c03f7d7687e2b6d74fb726c02515c7197ebf0/src/main/java/com/github/davidmoten/oas3/puml/ConverterMain.java#L39
OpenapiToPlantumlFormats: TypeAlias = Literal[
    "PUML",
    "EPS",
    "EPS_TEXT",
    "ATXT",
    "UTXT",
    "XMI_STANDARD",
    "XMI_STAR",
    "XMI_ARGO",
    # "SCXML",
    # "GRAPHML",
    # "PDF",
    # "MJPEG",
    # "ANIMATED_GIF",
    # "HTML",
    # "HTML5",
    "VDX",
    "LATEX",
    "LATEX_NO_PREAMBLE",
    # "BASE64",
    "BRAILLE_PNG",
    # "PREPROC",
    "DEBUG",
    "PNG",
    "RAW",
    "SVG",
]


class DownloadVerificationError(Exception):
    """Error thrown if download does not match hash."""


class OpenapiToPlantumlPaths(NamedTuple):
    jar_path: Path
    version_path: Path


def is_graphviz_installed() -> bool:
    """Check if grapthviz is installed.

    Returns
    -------
    bool
    """
    return which("dot") is not None


def is_java_installed() -> bool:
    """Check if grapthviz is installed.

    Returns
    -------
    bool
    """
    return which("java") is not None


def _get_latest_openapi_to_plantuml_version() -> str:
    """Get latest `openapi-to-plantuml` version on maven repo.

    Returns
    -------
    str
        Version string of latest `openapi-to-plantuml` release.

    Raises
    ------
    RuntimeError
        If version could not be found.
    """
    resp = httpx.get(f"{OPENAPI_TO_PLANTUML_MAVEN_URL}/maven-metadata.xml", follow_redirects=True)
    soup = BeautifulSoup(resp.content, features="xml")
    version = soup.find("latest")
    if version is None:
        msg = (
            "Could not find openapi-to-plantuml version in 'maven-metadata.xml':\n"
            f"{resp.content.decode()}"
        )
        raise RuntimeError(msg)
    return version.text


def _get_openapi_to_plantuml_download_url(version: str) -> str:
    """Get latest `openapi-to-plantuml` version on maven repo.

    Returns
    -------
    str
        Version string of latest `openapi-to-plantuml` release.

    Raises
    ------
    RuntimeError
        If version could not be found.
    """
    release_url = f"{OPENAPI_TO_PLANTUML_MAVEN_URL}/{version}"
    resp = httpx.get(release_url, follow_redirects=True)
    soup = BeautifulSoup(resp.content, features="lxml")
    links = soup.find_all("a")
    for link in links:
        if link["href"].endswith("with-dependencies.jar"):
            return f'{release_url}/{link["href"]}'
    msg = f"Could not find openapi-to-plantuml download link in:\n{resp.content.decode()}"
    raise RuntimeError(msg)


def get_openapi_to_plantuml_paths() -> OpenapiToPlantumlPaths:
    """Get paths to cached ``openapi-to-plantuml`` files.

    Returns
    -------
    OpenapiToPlantumlPaths
    """
    return OpenapiToPlantumlPaths(
        jar_path=CACHE_DIR / "openapi-to-plantuml.jar",
        version_path=CACHE_DIR / "openapi-to-plantuml.version",
    )


def download_openapi_to_plantuml(version: str = "0.1.28") -> Path:
    """Download ``openapi-to-plantuml`` jar file with dependencies to cache folder.

    Parameters
    ----------
    version : str
        Version to download. Defaults to "0.1.28"

    Returns
    -------
    Path
        Path to jar file.

    Raises
    ------
    DownloadVerificationError
        Error thrown if downloaded file does not match expected md5 hash.
    """
    jar_path, version_path = get_openapi_to_plantuml_paths()
    if (
        jar_path.is_file() is True
        and version_path.is_file() is True
        and version_path.read_text() == version
    ):
        return jar_path
    download_url = _get_openapi_to_plantuml_download_url(version)
    download_response = httpx.get(download_url, follow_redirects=True)
    expected_md5_hash = httpx.get(f"{download_url}.md5", follow_redirects=True)
    if md5(download_response.content).hexdigest() != expected_md5_hash.text:
        raise DownloadVerificationError
    jar_path.write_bytes(download_response.content)
    version_path.write_text(version)
    return jar_path


def run_openapi_to_plantuml(
    openapi_spec: Path,
    output_path: Path,
    mode: OpenapiToPlantumlModes,
    output_format: OpenapiToPlantumlFormats,
    version: str = "0.1.28",
) -> list[Path]:
    """_summary_

    Parameters
    ----------
    openapi_spec : Path
        _description_
    output_path : Path
        _description_
    mode : OpenapiToPlantumlModes
        _description_
    output_format : OpenapiToPlantumlFormats
        _description_
    version : str
        _description_. Defaults to "0.1.28"

    Returns
    -------
    list[Path]
        _description_
    """
    mode = cast(OpenapiToPlantumlModes, TypeAdapter(OpenapiToPlantumlModes).validate_python(mode))
    output_format = cast(
        OpenapiToPlantumlFormats,
        TypeAdapter(OpenapiToPlantumlFormats).validate_python(output_format),
    )
    jar_path = download_openapi_to_plantuml(version)
    java_path = which("java")
    assert java_path is not None
    with openapi_3_dot_1_compat(openapi_spec) as spec_file:
        subprocess.run(
            [
                java_path,
                "-jar",
                f"{jar_path.resolve().as_posix()}",
                mode,
                f"{spec_file.resolve().as_posix()}",
                output_format,
                f"{output_path.resolve().as_posix()}",
            ],
            check=True,
        )
    if mode == "single":
        return list(output_path.parent.glob("*"))
    return list(output_path.glob("*"))
