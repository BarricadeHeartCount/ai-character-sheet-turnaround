"""Backend resolver. Maps a backend name to a RenderBackend implementation."""
from __future__ import annotations

import logging

from config.schema import AppConfig

log = logging.getLogger("turnaround.services.registry")


def resolve_backend(config: AppConfig):
    """Return a RenderBackend for the configured backend name.

    Backends are imported lazily so the stub doesn't drag in torch.
    """
    name = config.render.backend
    if name == "stub":
        from services.stub_backend import StubBackend

        return StubBackend(config)
    if name == "remote_renderer":
        from services.remote_renderer import RemoteRenderer

        return RemoteRenderer(config)
    if name == "local_diffusion":
        from services.local_diffusion import LocalDiffusionBackend

        return LocalDiffusionBackend(config)
    raise ValueError(f"unknown backend: {name!r}")