"""Standard icon target sizes (NxN pixels)."""

from __future__ import annotations

TARGET_SIZES: tuple[int, ...] = (16, 24, 32, 48, 64, 128, 256)
DEFAULT_TARGET_SIZE: int = 32

MAX_SOURCE_SIZE: int = 512


def size_label(n: int) -> str:
    return f"{n}x{n} pixels"
