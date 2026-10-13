"""The turnaround engine: prompt → pose renders → composed sheet.

This is the heart of the tool. It is deliberately backend-agnostic: it talks
to a `RenderBackend` (see services/) and a `SheetComposer` (see utils/).
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

from config.schema import AppConfig
from core.prompt_builder import build_pose_prompt
from handlers.registry import Handler
from models.character import CharacterSpec
from models.sheet import TurnaroundSheet
from services.backend_registry import resolve_backend
from utils.sheet_composer import compose_sheet

log = logging.getLogger("turnaround.engine")


@dataclass(frozen=True)
class RenderResult:
    path: Path
    elapsed_ms: int
    pose_count: int


class TurnaroundEngine:
    """Coordinates prompt building, rendering, and sheet composition.

    Concurrency: single-threaded by design. The Qt shell runs this on a worker
    QThread via `handlers/`. Do not call from multiple threads.
    """

    def __init__(self, config: AppConfig, handlers: list[Handler] | None = None) -> None:
        self.config = config
        self.handlers = handlers or []
        self._backend = resolve_backend(config)

    def render_single(self, prompt: str, out_dir: Path) -> RenderResult:
        """Render one character and write a composed turnaround sheet to disk."""
        start = time.perf_counter()
        spec = CharacterSpec.from_prompt(prompt)
        log.info("character spec: %s", spec.name)

        images = []
        for pose in self.config.sheet.poses:
            pose_prompt = build_pose_prompt(spec, pose)
            log.debug("rendering pose=%s prompt=%r", pose, pose_prompt)
            img = self._backend.render(
                prompt=pose_prompt,
                width=self.config.render.width,
                height=self.config.render.height,
                seed=self.config.render.seed,
            )
            images.append((pose, img))

        sheet: TurnaroundSheet = compose_sheet(
            images=images,
            spec=spec,
            config=self.config.sheet,
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        sheet_path = out_dir / f"{spec.slug}_turnaround.png"
        sheet.save(sheet_path)

        elapsed = int((time.perf_counter() - start) * 1000)
        log.info("sheet written %s in %dms (%d poses)", sheet_path, elapsed, len(images))
        return RenderResult(path=sheet_path, elapsed_ms=elapsed, pose_count=len(images))