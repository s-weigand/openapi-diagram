"""Module to check and fetch openapi_to_plantuml."""

from __future__ import annotations

import subprocess
from hashlib import md5
from shutil import which
from typing import TYPE_CHECKING
from typing import Literal
from typing import TypeAlias
from typing import cast
from warnings import warn

import httpx
from bs4 import BeautifulSoup
from pydantic import TypeAdapter

from openapi_diagram import CACHE_DIR
from openapi_diagram import OPENAPI_TO_PLANTUML_DEFAULT_VERSION
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
    "puml",
    "eps",
    "eps_text",
    "atxt",
    "utxt",
    "xmi_standard",
    "xmi_star",
    "xmi_argo",
    # "scxml",
    # "graphml",
    # "pdf",
    # "mjpeg",
    # "animated_gif",
    # "html",
    # "html5",
    "vdx",
    "latex",
    "latex_no_preamble",
    # "base64",
    "braille_png",
    # "preproc",
    "debug",
    "png",
    "raw",
    "svg",
]


class DownloadVerificationError(Exception):
    """Error thrown if download does not match hash."""


class MissingDependecyError(RuntimeError):
    """Error thrown when an essential dependency is missing."""


class MissingDependecyWarning(UserWarning):
    """Warn when a non essential dependency is missing."""


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

    Parameters
    ----------
    version : str
        Version to download. Defaults to "0.1.28"

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


def get_openapi_to_plantuml_path(version: str = OPENAPI_TO_PLANTUML_DEFAULT_VERSION) -> Path:
    """Get path to cached ``openapi-to-plantuml`` file.

    Parameters
    ----------
    version : str
        Version to download. Defaults to "0.1.28"

    Returns
    -------
    Path
    """
    return CACHE_DIR / f"openapi-to-plantuml-{version}.jar"


def download_openapi_to_plantuml(version: str = OPENAPI_TO_PLANTUML_DEFAULT_VERSION) -> Path:
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
    jar_path = get_openapi_to_plantuml_path(version)
    if jar_path.is_file() is True:
        return jar_path
    download_url = _get_openapi_to_plantuml_download_url(version)
    download_response = httpx.get(download_url, follow_redirects=True)
    expected_md5_hash = httpx.get(f"{download_url}.md5", follow_redirects=True)
    if md5(download_response.content).hexdigest() != expected_md5_hash.text:
        msg = "Downloaded openapi-to-plantuml jar has invalid hash."
        raise DownloadVerificationError(msg)
    jar_path.write_bytes(download_response.content)
    return jar_path


def run_openapi_to_plantuml(
    openapi_spec: Path,
    output_path: Path,
    mode: OpenapiToPlantumlModes,
    diagram_format: OpenapiToPlantumlFormats,
    version: str = OPENAPI_TO_PLANTUML_DEFAULT_VERSION,
) -> list[Path]:
    """Run ``openapi-to-plantuml``.

    Parameters
    ----------
    openapi_spec : Path
        Spec file to use (only JSON and YAML) are supported.
    output_path : Path
        File (``mode='single'``) or folder (``mode='split'``) to write the output to.
    mode : OpenapiToPlantumlModes
        Mode to run
    diagram_format : OpenapiToPlantumlFormats
        Format the diagram/-s should be in.
    version : str
        Version of ``openapi-to-plantuml`` to use. Defaults to "0.1.28"

    Returns
    -------
    list[Path]
        List of created output files.

    Raises
    ------
    MissingDependecyError
        If the java installation can not be found.
    """
    mode = cast(OpenapiToPlantumlModes, TypeAdapter(OpenapiToPlantumlModes).validate_python(mode))
    diagram_format = cast(
        OpenapiToPlantumlFormats,
        TypeAdapter(OpenapiToPlantumlFormats).validate_python(diagram_format),
    )
    if which("dot") is None:
        msg = "Graphviz installation not found, some output formats might not be available."
        warn(MissingDependecyWarning(msg), stacklevel=2)
    java_path = which("java")
    if java_path is None:
        msg = "Can not run openapi-to-plantuml without java installed."
        raise MissingDependecyError(msg)

    jar_path = download_openapi_to_plantuml(version)
    if mode == "single":
        output_path.parent.mkdir(parents=True, exist_ok=True)
    with openapi_3_dot_1_compat(openapi_spec) as spec_file:
        subprocess.run(
            [
                java_path,
                "-jar",
                f"{jar_path.resolve().as_posix()}",
                mode,
                f"{spec_file.resolve().as_posix()}",
                diagram_format.upper(),
                f"{output_path.resolve().as_posix()}",
            ],
            check=True,
        )
    if mode == "single":
        return list(output_path.parent.glob(f"*.{diagram_format}"))
    return list(output_path.glob(f"*.{diagram_format}"))
