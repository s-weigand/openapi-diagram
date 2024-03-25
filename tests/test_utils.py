"""Tests for ``openapi_diagram.utils``."""

from __future__ import annotations

import json
from typing import Any

import yaml

from openapi_diagram.utils import openapi_3_dot_1_compat
from tests import TEST_DATA


def remove_titles_and_descriptions(spec: dict[str, Any]):
    """Helper to compare compat results ignoring different title and descriptions."""
    spec.pop("title", None)
    spec.pop("description", None)
    for value in spec.values():
        if isinstance(value, dict):
            remove_titles_and_descriptions(value)


def test_openapi_3_dot_1_compat():
    """Compat result is functionally equivalent."""
    desired_spec_file = TEST_DATA / "petstore-3-0.json"
    with openapi_3_dot_1_compat(TEST_DATA / "petstore-3-1.yaml") as spec_file:
        assert remove_titles_and_descriptions(
            yaml.safe_load(spec_file.read_text())
        ) == remove_titles_and_descriptions(json.loads(desired_spec_file.read_text()))


def test_openapi_3_dot_1_compat_no_op_json():
    """Json content does not get changed."""
    original_spec_file = TEST_DATA / "petstore-3-0.json"
    with openapi_3_dot_1_compat(original_spec_file) as spec_file:
        assert json.loads(spec_file.read_text()) == json.loads(original_spec_file.read_text())


def test_openapi_3_dot_1_compat_no_op_yaml():
    """Yaml content is equivalent to json one."""
    desired_spec_file = TEST_DATA / "petstore-3-0.json"
    with openapi_3_dot_1_compat(TEST_DATA / "petstore-3-0.yaml") as spec_file:
        assert yaml.safe_load(spec_file.read_text()) == json.loads(desired_spec_file.read_text())
