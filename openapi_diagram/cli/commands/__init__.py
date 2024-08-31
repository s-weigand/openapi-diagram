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
    typer.Option(
        "--openapi-spec",
        "-s",
        exists=True,
        help="Spec file to use (only JSON and YAML) are supported.",
        envvar="OPENAPI_DIAGRAM_SPEC_FILE_PATH",
    ),
]

OutputPath = Annotated[
    Path,
    typer.Option(
        "--output-path",
        "-o",
        help="File (``mode='single'``) or folder (``mode='split'``) to write the output to.",
        envvar="OPENAPI_DIAGRAM_OUTPUT_PATH",
    ),
]
Mode = Annotated[
    ModesEnum,
    typer.Option(
        "--mode",
        "-m",
        help=(
            "Mode to run openapi-to-plantuml in. "
            "Where 'single' creates one diagram and 'split' creates a diagram per route."
        ),
        envvar="OPENAPI_DIAGRAM_MODE",
    ),
]
DiagramFormat = Annotated[
    FormatsEnum,
    typer.Option(
        "--diagram-format",
        "-d",
        help="Format the diagram should be in.",
        envvar="OPENAPI_DIAGRAM_FORMAT",
    ),
]
