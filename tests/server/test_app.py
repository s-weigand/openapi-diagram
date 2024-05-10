"""Tests for ``openapi_diagram.server.app``."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING
from zipfile import ZipFile

from tests import TEST_DATA

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_single_diagram(app_client: TestClient):
    """Create diagram file for openapi spec file."""
    openapi_spec = TEST_DATA / "petstore-3-0.json"
    expected = TEST_DATA / "petstore.puml"
    resp = app_client.post(
        "/api/v1/create-diagrams",
        json={
            "fileName": openapi_spec.name,
            "fileContent": openapi_spec.read_text(),
            "mode": "single",
            "diagramFormat": "puml",
        },
    )
    assert resp.status_code == 200
    with ZipFile(BytesIO(resp.content)) as zip_resp:
        assert zip_resp.read("petstore-3-0.puml").rstrip(b"\n") == expected.read_bytes().rstrip(
            b"\n"
        )


def test_create_multiple_diagrams(app_client: TestClient):
    """Create multiple diagrams file for openapi spec file."""
    openapi_spec = TEST_DATA / "petstore-3-0.json"
    resp = app_client.post(
        "/api/v1/create-diagrams",
        json={
            "fileName": openapi_spec.name,
            "fileContent": openapi_spec.read_text(),
            "mode": "split",
            "diagramFormat": "puml",
        },
    )
    assert resp.status_code == 200
    with ZipFile(BytesIO(resp.content)) as zip_resp:
        assert len(zip_resp.namelist()) == 19, zip_resp.namelist()
