"""Request models for the REAT API."""

from __future__ import annotations

from pathlib import Path  # noqa: TCH003

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic.alias_generators import to_camel

from openapi_diagram import SUPPORTED_SPEC_FILE_FORMATS
from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlFormats  # noqa: TCH001
from openapi_diagram.openapi_to_plantuml import OpenapiToPlantumlModes  # noqa: TCH001


class CreateDiagram(BaseModel):
    """Request data to create diagrams."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    file_name: Path
    file_content: str
    mode: OpenapiToPlantumlModes
    diagram_format: OpenapiToPlantumlFormats

    @field_validator("file_name")
    @classmethod
    def validate_file_format(cls, value: Path) -> Path:  # noqa: DOC
        """Validate that the file has the correct format by checking its extension."""
        if value.suffix not in SUPPORTED_SPEC_FILE_FORMATS:
            msg = (
                "Only the following formats/extension are supported: "
                f"{', '.join(SUPPORTED_SPEC_FILE_FORMATS)!r} but got {value.name!r}."
            )
            raise ValueError(msg)
        return value
