"""Command to create diagram/-s from openapi spec file."""

from __future__ import annotations

import sys
from pathlib import Path  # noqa: TCH003
from typing import get_args

import typer

from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlFormats
from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlModes
from openapi_diagram.openapi_to_plantuml import run_openapi_to_plantuml

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum."""


ModesEnum = StrEnum("ModesEnum", get_args(OpenapiToPlantumlModes))  # type:ignore[call-overload]
FormatsEnum = StrEnum("Formats", get_args(OpenapiToPlantumlFormats))  # type:ignore[call-overload]


def create(
    openapi_spec: Path = typer.Option(
        exists=True, help="Spec file to use (only JSON and YAML) are supported."
    ),
    output_path: Path = typer.Option(
        help="File (``mode='single'``) or folder (``mode='split'``) to write the output to.",
    ),
    mode: ModesEnum = typer.Option(),  # type:ignore[valid-type]
    output_format: FormatsEnum = typer.Option(),  # type:ignore[valid-type]
    version: str = "0.1.28",
):
    """Create diagram/-s from openapi spec file."""
    run_openapi_to_plantuml(
        openapi_spec,
        output_path,
        mode.value,  # type:ignore[attr-defined]
        output_format.value.upper(),  # type:ignore[attr-defined]
        version,
    )
