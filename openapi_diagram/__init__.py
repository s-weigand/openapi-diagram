"""Top-level package for openapi-diagram."""

from __future__ import annotations

from pathlib import Path

from platformdirs import user_cache_dir

CACHE_DIR = Path(user_cache_dir("openapi-diagram", ensure_exists=True))

__author__ = """Sebastian Weigand"""
__email__ = "s.weigand.phy@gmail.com"
__version__ = "0.0.1"