"""Command to fetch diagrams from a openapi-diagram server."""

from __future__ import annotations

from io import BytesIO
from typing import Annotated
from zipfile import ZipFile

import httpx
import typer
from rich.console import Console

from openapi_diagram.cli.commands import DiagramFormat  # noqa: TCH001
from openapi_diagram.cli.commands import Mode  # noqa: TCH001
from openapi_diagram.cli.commands import OpenapiSpec  # noqa: TCH001
from openapi_diagram.cli.commands import OutputPath  # noqa: TCH001
from openapi_diagram.server.models.request_models import CreateDiagram


def fetch(
    openapi_spec: OpenapiSpec,
    output_path: OutputPath,
    mode: Mode,
    diagram_format: DiagramFormat,
    base_url: Annotated[
        str,
        typer.Option(
            "--base-url",
            "-u",
            help="Base url of the openapi-diagram server.",
            envvar="OPENAPI_DIAGRAM_FETCH_URL",
        ),
    ],
    max_timeout: Annotated[
        int,
        typer.Option(
            "--max-timeout",
            "-t",
            help="Maximum time to wai for server response.",
            envvar="OPENAPI_DIAGRAM_FETCH_TIMEOUT",
        ),
    ] = 30,
):
    """Fetch diagram from openapi-diagram server."""
    console = Console()
    request_data = CreateDiagram(
        file_name=openapi_spec,
        file_content=openapi_spec.read_text(),
        mode=mode.value,
        diagram_format=diagram_format.value,
    )
    with console.status("[bold green]Fetching diagrams..."):
        resp = httpx.post(
            f"{base_url.rstrip('/')}/api/v1/create-diagrams",
            json=request_data.model_dump(mode="json", by_alias=True),
            timeout=max_timeout,
        )
    if resp.status_code != 200:
        raise typer.Exit(1)

    with ZipFile(BytesIO(resp.content)) as zip_resp:
        if mode.value == "single":
            output_path.parent.mkdir(parents=True, exist_ok=True)
            diagram_zip_info = zip_resp.filelist[0]
            diagram_zip_info.filename = output_path.name
            zip_resp.extract(diagram_zip_info, output_path.parent)
        else:
            output_path.mkdir(parents=True, exist_ok=True)
            zip_resp.extractall(output_path)
