"""Command to create diagram/-s from openapi spec file."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path  # noqa: TCH003
from typing import get_args

import typer

from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlFormats
from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlModes
from openapi_diagram.openapi_to_plantuml import run_openapi_to_plantuml

ModesEnum = StrEnum("ModesEnum", get_args(OpenapiToPlantumlModes))  # type:ignore[misc]
FormatsEnum = StrEnum("Formats", get_args(OpenapiToPlantumlFormats))  # type:ignore[misc]


def create(
    openapi_spec: Path = typer.Option(
        exists=True, help="Spec file to use (only JSON and YAML) are supported."
    ),
    output_path: Path = typer.Option(
        help="File (``mode='single'``) or folder (``mode='split'``) to write the output to.",
    ),
    mode: ModesEnum = typer.Option(),
    output_format: FormatsEnum = typer.Option(),
    version: str = "0.1.28",
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
