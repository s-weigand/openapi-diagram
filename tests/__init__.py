"""Unit test package for openapi_diagram."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TEST_DATA = REPO_ROOT / "tests/data"

RUN_SLOW_TEST = (
    os.getenv("CI", None) is not None
    and os.getenv("OPENAPI_DIAGRAM__RUN_SLOW_TESTS", None) is not None
)
