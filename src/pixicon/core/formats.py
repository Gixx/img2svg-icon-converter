"""Supported image formats and helpers."""

from __future__ import annotations

from pathlib import Path

# Pillow-backed formats suitable for icon sources
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".bmp",
        ".tif",
        ".tiff",
        ".ico",
    }
)

FILE_DIALOG_FILTER = (
    "Images ("
    "*.png *.jpg *.jpeg *.gif *.webp *.bmp *.tif *.tiff *.ico"
    ");;All files (*.*)"
)


def is_supported(path: Path | str) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS
