"""HTTP backend that POSTs a prompt to a user-controlled render endpoint.

Compatible with a minimal ComfyUI-style /prompt endpoint and with the
`autograd-node` reference server. Endpoint must be set in config and must
match the allowlist pattern (localhost or explicit https).
"""
from __future__ import annotations

import base64
import io
import logging
from urllib.parse import urlparse

import httpx
from PIL import Image

from config.schema import AppConfig

log = logging.getLogger("turnaround.services.remote")

_ALLOWED_SCHEMES = {"http", "https"}
_ALLOWED_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


class RemoteRenderer:
    def __init__(self, config: AppConfig, timeout_s: float = 120.0) -> None:
        if not config.remote_endpoint:
            raise ValueError("remote_renderer backend requires config.remote_endpoint")
        parsed = urlparse(config.remote_endpoint)
        if parsed.scheme not in _ALLOWED_SCHEMES:
            raise ValueError(f"unsupported scheme: {parsed.scheme!r}")
        if parsed.scheme == "http" and parsed.hostname not in _ALLOWED_LOCAL_HOSTS:
            raise ValueError("plain http is only allowed for localhost endpoints")
        self.config = config
        self._client = httpx.Client(timeout=timeout_s)

    def render(self, prompt: str, width: int, height: int, seed: int = -1) -> Image.Image:
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": self.config.render.steps,
            "cfg_scale": self.config.render.cfg_scale,
            "sampler": self.config.render.sampler,
            "seed": seed,
        }
        log.debug("POST %s/prompt", self.config.remote_endpoint)
        resp = self._client.post(f"{self.config.remote_endpoint}/prompt", json=payload)
        resp.raise_for_status()
        body = resp.json()
        if "image_b64" not in body:
            raise RuntimeError("remote renderer returned no image_b64 field")
        raw = base64.b64decode(body["image_b64"])
        return Image.open(io.BytesIO(raw)).convert("RGBA")