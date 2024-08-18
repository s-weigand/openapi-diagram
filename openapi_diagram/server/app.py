"""REST API module."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from openapi_diagram.openapi_to_plantuml import run_openapi_to_plantuml
from openapi_diagram.server.models.request_models import CreateDiagram  # noqa: TCH001

app = FastAPI()


@app.post("/api/v1/create-diagrams")
async def create_diagrams(create_data: CreateDiagram):
    """Create openapi diagram/-s and return a zip file."""
    buffer = BytesIO()
    with (
        ZipFile(buffer, "a", ZIP_DEFLATED) as zipfile,
        TemporaryDirectory(prefix="openapi-diagram") as tmp_dir,
    ):
        output_path = Path(tmp_dir) / "output"
        if create_data.mode == "single":
            output_path = (
                output_path / f"{create_data.file_name.stem}.{create_data.diagram_format}"
            )
        spec_file = Path(tmp_dir) / create_data.file_name
        spec_file.write_text(create_data.file_content)
        files = run_openapi_to_plantuml(
            openapi_spec=spec_file,
            output_path=output_path,
            mode=create_data.mode,
            diagram_format=create_data.diagram_format,
        )
        for file in files:
            zipfile.writestr(file.name, file.read_text())

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/x-zip-compressed",
        headers={
            "Content-Disposition": f'attachment; filename="{create_data.file_name.stem}.zip"'
        },
    )
