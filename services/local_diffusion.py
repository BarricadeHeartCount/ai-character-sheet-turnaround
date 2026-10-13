"""Local diffusion backend.

This module is intentionally thin: it does not bundle a diffusion stack.
Instead it expects a user-installed `diffusers` pipeline to be importable and
a `.safetensors` checkpoint in `config.render.weights_dir`. If either is
missing, construction raises a clear error.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image

from config.schema import AppConfig

log = logging.getLogger("turnaround.services.local")


class LocalDiffusionBackend:
    def __init__(self, config: AppConfig) -> None:
        try:
            import torch  # noqa: F401
            from diffusers import StableDiffusionXLPipeline  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "local_diffusion backend requires `torch` and `diffusers`. "
                "Install them with: pip install torch diffusers accelerate safetensors"
            ) from exc

        weights_dir: Path = config.render.weights_dir
        if not weights_dir.exists():
            raise RuntimeError(f"weights dir not found: {weights_dir}")

        self.config = config
        self._pipe = None  # constructed lazily on first render

    def _ensure_pipeline(self) -> None:
        if self._pipe is not None:
            return
        from diffusers import StableDiffusionXLPipeline
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        log.info("loading SDXL pipeline on %s (%s)", device, dtype)
        self._pipe = StableDiffusionXLPipeline.from_pretrained(
            str(self.config.render.weights_dir),
            torch_dtype=dtype,
            use_safetensors=True,
        ).to(device)

    def render(self, prompt: str, width: int, height: int, seed: int = -1) -> Image.Image:
        self._ensure_pipeline()
        import torch

        generator = None
        if seed >= 0:
            generator = torch.Generator(device=self._pipe.device).manual_seed(seed)
        result = self._pipe(
            prompt=prompt,
            width=width,
            height=height,
            num_inference_steps=self.config.render.steps,
            guidance_scale=self.config.render.cfg_scale,
            generator=generator,
        )
        img = result.images[0]
        return img.convert("RGBA") if img.mode != "RGBA" else img