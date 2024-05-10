"""Command to create diagram/-s from openapi spec file."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path  # noqa: TCH003
from typing import Annotated
from typing import get_args

import typer

from openapi_diagram import OPENAPI_TO_PLANTUML_DEFAULT_VERSION
from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlFormats
from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlModes
from openapi_diagram.openapi_to_plantuml import run_openapi_to_plantuml

ModesEnum = StrEnum("ModesEnum", get_args(OpenapiToPlantumlModes))  # type:ignore[misc]
FormatsEnum = StrEnum("Formats", get_args(OpenapiToPlantumlFormats))  # type:ignore[misc]


def create(
    openapi_spec: Annotated[
        Path,
        typer.Option(exists=True, help="Spec file to use (only JSON and YAML) are supported."),
    ],
    output_path: Annotated[
        Path,
        typer.Option(
            help="File (``mode='single'``) or folder (``mode='split'``) to write the output to.",
        ),
    ],
    mode: Annotated[ModesEnum, typer.Option()],
    output_format: Annotated[FormatsEnum, typer.Option()],
    version: Annotated[str, typer.Option()] = OPENAPI_TO_PLANTUML_DEFAULT_VERSION,
):
    """Create diagram/-s from openapi spec file."""
    run_openapi_to_plantuml(
        openapi_spec,
        output_path,
        mode.value,  # type:ignore[arg-type]
        output_format.value,  # type:ignore[arg-type]
        version,
    )
    raise typer.Exit(0)
