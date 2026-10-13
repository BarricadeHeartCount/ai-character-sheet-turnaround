"""Deterministic stub backend.

Produces a solid-color frame with the pose name rendered as text. Used for
tests, CI, and headless batch runs where a real diffusion backend isn't
available. Never removed — the whole test suite depends on this.
"""
from __future__ import annotations

import hashlib
import logging

from PIL import Image, ImageDraw

from config.schema import AppConfig

log = logging.getLogger("turnaround.services.stub")


class StubBackend:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def render(self, prompt: str, width: int, height: int, seed: int = -1) -> Image.Image:
        digest = hashlib.sha256(prompt.encode("utf-8")).digest()
        bg = (digest[0], digest[1], digest[2], 255)
        img = Image.new("RGBA", (width, height), bg)
        draw = ImageDraw.Draw(img)
        # Cheap label so tests can assert on image content if needed.
        label = prompt[:60]
        draw.text((16, 16), label, fill=(255, 255, 255, 255))
        log.debug("stub render %dx%d seed=%s", width, height, seed)
        return img