"""Unit tests for Pixicon core conversion."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from pixicon.core.convert import (
    convert_file,
    image_to_svg,
    pick_ico_size,
    prepare_image,
)
from pixicon.core.validate import ValidationError, validate_image


def _solid(size: int, color: tuple[int, int, int, int] = (255, 0, 0, 255)) -> Image.Image:
    return Image.new("RGBA", (size, size), color)


def test_validate_square_ok() -> None:
    info = validate_image(_solid(64))
    assert info.width == 64


def test_validate_rejects_non_square() -> None:
    with pytest.raises(ValidationError, match="square"):
        validate_image(Image.new("RGBA", (64, 32), (0, 0, 0, 255)))


def test_validate_rejects_too_large() -> None:
    with pytest.raises(ValidationError, match="too large"):
        validate_image(_solid(513))


def test_image_to_svg_resizes_nearest() -> None:
    # 2x2 red/blue checker → 2x2 SVG after target 2
    im = Image.new("RGBA", (2, 2))
    im.putpixel((0, 0), (255, 0, 0, 255))
    im.putpixel((1, 0), (0, 0, 255, 255))
    im.putpixel((0, 1), (0, 0, 255, 255))
    im.putpixel((1, 1), (255, 0, 0, 255))
    svg = image_to_svg(im, target_size=2)
    assert 'width="2"' in svg
    assert "shape-rendering=\"crispEdges\"" in svg
    assert "#ff0000" in svg
    assert "#0000ff" in svg


def test_transparent_pixels_skipped() -> None:
    im = Image.new("RGBA", (2, 2), (0, 0, 0, 0))
    im.putpixel((0, 0), (0, 255, 0, 255))
    svg = image_to_svg(im, target_size=2)
    assert svg.count("<rect") == 1
    assert "#00ff00" in svg


def test_convert_file(tmp_path: Path) -> None:
    src = tmp_path / "icon.png"
    dst = tmp_path / "icon.svg"
    _solid(32, (10, 20, 30, 255)).save(src)
    convert_file(src, dst, target_size=16)
    text = dst.read_text(encoding="utf-8")
    assert text.startswith("<svg")
    assert 'width="16"' in text


def test_pick_ico_size_prefers_exact() -> None:
    assert pick_ico_size([16, 32, 48, 256], target_size=32) == 32
    # tie on distance → prefer larger embedded size
    assert pick_ico_size([16, 48, 256], target_size=32) == 48


def test_ico_uses_embedded_size_not_largest(tmp_path: Path) -> None:
    """Multi-size ICO must not use a large opaque frame when 32px exists."""
    src = Path("tmp/ico-samples/w2k_cd-rom_drive.ico")
    if not src.is_file():
        pytest.skip("sample ICO not present")
    dst = tmp_path / "out.svg"
    convert_file(src, dst, target_size=32)
    text = dst.read_text(encoding="utf-8")
    assert "#800000" not in text
    with Image.open(src) as im:
        prepared = prepare_image(im, target_size=32)
    assert prepared.size == (32, 32)
    assert prepared.getpixel((0, 0))[3] == 0
