"""Package with cli command modules."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Annotated
from typing import get_args

import typer

from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlFormats
from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlModes

ModesEnum = StrEnum("ModesEnum", get_args(OpenapiToPlantumlModes))  # type:ignore[misc]
FormatsEnum = StrEnum("Formats", get_args(OpenapiToPlantumlFormats))  # type:ignore[misc]

OpenapiSpec = Annotated[
    Path,
    typer.Option(exists=True, help="Spec file to use (only JSON and YAML) are supported."),
]

OutputPath = Annotated[
    Path,
    typer.Option(
        help="File (``mode='single'``) or folder (``mode='split'``) to write the output to.",
    ),
]
Mode = Annotated[
    ModesEnum,
    typer.Option(
        help=(
            "Mode to run openapi-to-plantuml in. "
            "Where 'single' creates one diagram and 'split' creates a diagram per route."
        )
    ),
]
DiagramFormat = Annotated[FormatsEnum, typer.Option(help="Format the diagram should be in.")]
