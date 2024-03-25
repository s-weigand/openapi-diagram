"""Pytest config and fixture definitions."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING
from typing import Any

import pytest

from openapi_diagram.openapi_to_plantuml import download_openapi_to_plantuml
from tests import TEST_DATA

if TYPE_CHECKING:
    from pathlib import Path


@contextmanager
def monkeypatch_all(monkeypatch: pytest.MonkeyPatch, name: str, value: Any):
    """Context to monkeypatch all usages across modules."""
    with monkeypatch.context() as m:
        for module_name, module in sys.modules.items():
            if module_name.startswith("openapi_diagram") and hasattr(module, name):
                m.setattr(module, name, value)
        yield


@pytest.fixture()
def _mock_empty_path(monkeypatch: pytest.MonkeyPatch):
    """Set PATH environment variale to empty value."""
    with monkeypatch.context() as m:
        m.setenv("PATH", "")
        yield


@pytest.fixture()
def mock_cache_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Replace CACHDIR with mock path inside of ``tmp_path``."""
    mock_path = tmp_path / ".cache"
    mock_path.mkdir(parents=True, exist_ok=True)
    with monkeypatch_all(monkeypatch, "CACHE_DIR", mock_path):
        yield mock_path


@pytest.fixture(autouse=True)
def cached_openapi_to_plantuml(monkeypatch: pytest.MonkeyPatch):
    """Download and monkeypath jar to use cached version."""
    mock_path = TEST_DATA / ".cache"
    mock_path.mkdir(parents=True, exist_ok=True)
    with monkeypatch_all(monkeypatch, "CACHE_DIR", mock_path):
        download_openapi_to_plantuml()
        yield mock_path
