"""Pixel-preserving image → SVG conversion (from gif2svg)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from pixicon.core.sizes import MAX_SOURCE_SIZE
from pixicon.core.validate import validate_image


def rgba_to_fill(r: int, g: int, b: int, a: int) -> str:
    if a >= 255:
        return f"#{r:02x}{g:02x}{b:02x}"
    return f"rgba({r},{g},{b},{a / 255:.4f})"


def collect_rects(
    im: Image.Image,
    *,
    alpha_threshold: int = 0,
) -> list[tuple[int, int, int, int, str]]:
    """Build merged rectangles (x, y, w, h, fill) from visible pixels."""
    rgba = im.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()

    rows: list[list[tuple[int, int, int, str]]] = []
    for y in range(height):
        row: list[tuple[int, int, int, str]] = []
        x = 0
        while x < width:
            r, g, b, a = pixels[x, y]
            if a <= alpha_threshold:
                x += 1
                continue
            fill = rgba_to_fill(r, g, b, a)
            x0 = x
            x += 1
            while x < width:
                r2, g2, b2, a2 = pixels[x, y]
                if a2 <= alpha_threshold or rgba_to_fill(r2, g2, b2, a2) != fill:
                    break
                x += 1
            row.append((x0, x - x0, y, fill))
        rows.append(row)

    active: dict[tuple[int, int, str], list[int | str]] = {}
    done: list[tuple[int, int, int, int, str]] = []

    for rects in rows:
        seen: set[tuple[int, int, str]] = set()
        for x, rw, y, fill in rects:
            key = (x, rw, fill)
            seen.add(key)
            if key in active:
                active[key][3] = int(active[key][3]) + 1
            else:
                active[key] = [x, y, rw, 1, fill]
        for key in list(active):
            if key not in seen:
                item = active.pop(key)
                done.append(
                    (
                        int(item[0]),
                        int(item[1]),
                        int(item[2]),
                        int(item[3]),
                        str(item[4]),
                    )
                )

    for item in active.values():
        done.append(
            (
                int(item[0]),
                int(item[1]),
                int(item[2]),
                int(item[3]),
                str(item[4]),
            )
        )

    return done


def frame_count(im: Image.Image) -> int:
    n = getattr(im, "n_frames", 1)
    return int(n) if n else 1


def load_frame(im: Image.Image, index: int = 0) -> Image.Image:
    try:
        im.seek(index)
    except EOFError as exc:
        raise ValueError(
            f"frame {index} does not exist (n_frames={frame_count(im)})"
        ) from exc
    return im.convert("RGBA").copy()


def ico_square_sizes(im: Image.Image) -> list[int]:
    """Return sorted unique square edge lengths embedded in an ICO."""
    ico = getattr(im, "ico", None)
    if ico is None:
        return []
    sizes_fn = getattr(ico, "sizes", None)
    if sizes_fn is None:
        return []
    return sorted({w for w, h in sizes_fn() if w == h and w >= 1})


def pick_ico_size(edges: list[int], *, target_size: int) -> int:
    """Prefer exact target, else closest square size within MAX_SOURCE_SIZE."""
    allowed = [e for e in edges if e <= MAX_SOURCE_SIZE]
    pool = allowed or edges
    if not pool:
        raise ValueError("ICO contains no usable square sizes")
    if target_size in pool:
        return target_size
    return min(pool, key=lambda e: (abs(e - target_size), -e))


def prepare_image(
    im: Image.Image,
    *,
    target_size: int,
    frame: int = 0,
) -> Image.Image:
    """
    Load a single RGBA raster ready for conversion.

    For multi-resolution ICO files, pick the embedded size closest to
    ``target_size`` (exact match preferred). Pillow's default ICO frame is
    often the largest size, which may lack a proper transparency mask.
    """
    edges = ico_square_sizes(im)
    if edges:
        chosen = pick_ico_size(edges, target_size=target_size)
        return im.ico.getimage((chosen, chosen)).convert("RGBA")  # type: ignore[union-attr]

    if frame_count(im) > 1 or getattr(im, "is_animated", False):
        return load_frame(im, frame)
    return im.convert("RGBA")


def source_pixel_size(path: Path) -> tuple[int, int]:
    """Display size for the source list (ICO: largest square <= max)."""
    with Image.open(path) as im:
        edges = ico_square_sizes(im)
        if edges:
            allowed = [e for e in edges if e <= MAX_SOURCE_SIZE]
            edge = max(allowed or edges)
            return edge, edge
        w, h = im.size
        return int(w), int(h)


def rects_to_svg(
    rects: list[tuple[int, int, int, int, str]],
    width: int,
    height: int,
) -> str:
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" shape-rendering="crispEdges">',
    ]
    for x, y, rw, rh, fill in rects:
        lines.append(
            f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="{fill}"/>'
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def image_to_svg(
    im: Image.Image,
    *,
    target_size: int,
    alpha_threshold: int = 0,
) -> str:
    """Validate, nearest-neighbor resize to target_size, emit SVG."""
    rgba = im.convert("RGBA")
    validate_image(rgba)
    if target_size < 1:
        raise ValueError("target_size must be >= 1")
    if rgba.size != (target_size, target_size):
        rgba = rgba.resize(
            (target_size, target_size),
            Image.Resampling.NEAREST,
        )
    rects = collect_rects(rgba, alpha_threshold=alpha_threshold)
    return rects_to_svg(rects, target_size, target_size)


def convert_image(
    im: Image.Image,
    *,
    target_size: int,
    alpha_threshold: int = 0,
    frame: int = 0,
) -> str:
    """Convert a Pillow image (ICO / GIF / still) to SVG markup."""
    prepared = prepare_image(im, target_size=target_size, frame=frame)
    return image_to_svg(
        prepared,
        target_size=target_size,
        alpha_threshold=alpha_threshold,
    )


def convert_file(
    src: Path,
    dst: Path,
    *,
    target_size: int,
    alpha_threshold: int = 0,
    frame: int = 0,
) -> Path:
    """Convert one image file to an SVG file. Returns dst."""
    with Image.open(src) as im:
        svg = convert_image(
            im,
            target_size=target_size,
            alpha_threshold=alpha_threshold,
            frame=frame,
        )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(svg, encoding="utf-8")
    return dst
