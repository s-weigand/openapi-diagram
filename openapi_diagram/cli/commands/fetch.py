"""Command to fetch diagrams from a openapi-diagram server."""

from __future__ import annotations

from io import BytesIO
from typing import Annotated
from zipfile import ZipFile

import httpx
import typer  # noqa: TCH002

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
    base_url: Annotated[str, typer.Option(help="Base url of the openapi-diagram server.")],
):
    """Fetch diagram from openapi-diagram server."""
    request_data = CreateDiagram(
        file_name=openapi_spec,
        file_content=openapi_spec.read_text(),
        mode=mode.value,
        diagram_format=diagram_format.value,
    )
    resp = httpx.post(
        f"{base_url.rstrip('/')}/api/v1/create-diagrams",
        json=request_data.model_dump(mode="json", by_alias=True),
    )

    with ZipFile(BytesIO(resp.content)) as zip_resp:
        if mode.value == "single":
            output_path.parent.mkdir(parents=True, exist_ok=True)
            diagram_zip_info = zip_resp.filelist[0]
            diagram_zip_info.filename = output_path.name
            zip_resp.extract(diagram_zip_info, output_path.parent)
        else:
            output_path.mkdir(parents=True, exist_ok=True)
            zip_resp.extractall(output_path)
