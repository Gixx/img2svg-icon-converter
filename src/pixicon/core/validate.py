"""Source image validation rules."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from pixicon.core.sizes import MAX_SOURCE_SIZE


class ValidationError(ValueError):
    """Raised when a source image does not meet Pixicon requirements."""


@dataclass(frozen=True)
class ImageInfo:
    width: int
    height: int


def validate_image(im: Image.Image) -> ImageInfo:
    """Require a square image with each side <= MAX_SOURCE_SIZE."""
    width, height = im.size
    if width != height:
        raise ValidationError(
            f"image must be square (got {width}x{height})"
        )
    if width > MAX_SOURCE_SIZE or height > MAX_SOURCE_SIZE:
        raise ValidationError(
            f"image too large (max {MAX_SOURCE_SIZE}x{MAX_SOURCE_SIZE}, "
            f"got {width}x{height})"
        )
    if width < 1 or height < 1:
        raise ValidationError("image has invalid dimensions")
    return ImageInfo(width=width, height=height)
