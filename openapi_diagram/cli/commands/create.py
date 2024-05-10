"""Command to create diagram/-s from openapi spec file."""

from __future__ import annotations

from typing import Annotated

import typer

from openapi_diagram import OPENAPI_TO_PLANTUML_DEFAULT_VERSION
from openapi_diagram.cli.commands import DiagramFormat  # noqa: TCH001
from openapi_diagram.cli.commands import Mode  # noqa: TCH001
from openapi_diagram.cli.commands import OpenapiSpec  # noqa: TCH001
from openapi_diagram.cli.commands import OutputPath  # noqa: TCH001
from openapi_diagram.openapi_to_plantuml import run_openapi_to_plantuml


def create(
    openapi_spec: OpenapiSpec,
    output_path: OutputPath,
    mode: Mode,
    diagram_format: DiagramFormat,
    version: Annotated[str, typer.Option()] = OPENAPI_TO_PLANTUML_DEFAULT_VERSION,
):
    """Create diagram/-s from openapi spec file."""
    run_openapi_to_plantuml(
        openapi_spec,
        output_path,
        mode.value,  # type:ignore[arg-type]
        diagram_format.value,  # type:ignore[arg-type]
        version,
    )
    raise typer.Exit(0)
