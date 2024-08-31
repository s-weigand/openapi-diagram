"""Top-level package for openapi-diagram."""

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_cache_dir

CACHE_DIR = Path(user_cache_dir("openapi-diagram", ensure_exists=True))

OPENAPI_TO_PLANTUML_DEFAULT_VERSION = os.getenv("OPENAPI_DIAGRAM_O2P_VERSION", "0.1.28")
SUPPORTED_SPEC_FILE_FORMATS = (".json", ".yaml", ".yml")

__author__ = """Sebastian Weigand"""
__email__ = "s.weigand.phy@gmail.com"
__version__ = "0.0.1"
