"""Handler: sample a dominant color palette from a rendered sheet."""
from __future__ import annotations

import logging
from pathlib import Path

from handlers.registry import HandlerEntry
from utils.color import dominant_palette
from utils.image_io import load_image

log = logging.getLogger("turnaround.handlers.palette")


def run(engine, *, sheet_path: Path | str, k: int = 8, out_dir: Path | None = None, **_ignored) -> Path:
    """Extract a k-color palette from a sheet and write it as a swatch strip PNG."""
    from PIL import Image

    img = load_image(Path(sheet_path))
    palette = dominant_palette(img, k=k)
    strip_w = 64 * len(palette)
    strip = Image.new("RGBA", (strip_w, 96), (255, 255, 255, 255))
    for i, rgb in enumerate(palette):
        block = Image.new("RGBA", (64, 96), (*rgb, 255))
        strip.paste(block, (i * 64, 0))

    out = (out_dir or engine.config.output_dir) / f"{Path(sheet_path).stem}_palette.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    strip.save(out)
    log.info("palette strip: %s (%d colors)", out, len(palette))
    return out


HANDLER = HandlerEntry(
    name="palette_extract",
    description="Sample a dominant color palette from a rendered sheet.",
    run=run,
    order=30,
)