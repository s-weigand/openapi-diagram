"""Tests for ``openapi_diagram.server.models.request_models``."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from openapi_diagram.server.models.request_models import CreateDiagram


@pytest.mark.parametrize("file_extension", ["json", "yml", "yaml"])
def test_validate_file_name(file_extension: str):
    """No exceptions on valid formats."""
    CreateDiagram.model_validate(
        {
            "fileName": f"spec_file.{file_extension}",
            "fileContent": "",
            "mode": "single",
            "diagramFormat": "svg",
        }
    )


def test_validate_file_name_error():
    """Raise validation error on invalida file name."""
    with pytest.raises(ValidationError) as execinfo:
        CreateDiagram.model_validate(
            {
                "fileName": "spec_file.not_supported",
                "fileContent": "",
                "mode": "single",
                "diagramFormat": "svg",
            }
        )
    assert (
        "Only the following formats/extension are supported: "
        "'.json, .yaml, .yml' but got 'spec_file.not_supported'."
    ) in str(execinfo.value)
