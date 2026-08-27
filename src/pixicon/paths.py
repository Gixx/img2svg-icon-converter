"""Resolve resource paths for source runs and frozen builds."""

from __future__ import annotations

import sys
from pathlib import Path


def resource_root() -> Path:
    """Return directory that contains the ``assets`` folder."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    # src/pixicon/paths.py → repo root
    return Path(__file__).resolve().parents[2]


def asset_path(*parts: str) -> Path:
    return resource_root() / "assets" / Path(*parts)
