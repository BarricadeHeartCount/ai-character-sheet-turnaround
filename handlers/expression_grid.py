"""Handler: render an expression grid for an existing character spec."""
from __future__ import annotations

import logging
from pathlib import Path

from core.prompt_builder import build_pose_prompt
from handlers.registry import HandlerEntry
from models.character import CharacterSpec
from utils.sheet_composer import compose_grid

log = logging.getLogger("turnaround.handlers.expressions")

_DEFAULT_EXPRESSIONS = ["neutral", "smile", "frown", "surprise", "anger", "smirk"]


def run(engine, *, prompt: str, expressions: list[str] | None = None, out_dir: Path | None = None) -> Path:
    """Render a 2xN expression grid for the given character prompt."""
    spec = CharacterSpec.from_prompt(prompt)
    faces = expressions or _DEFAULT_EXPRESSIONS
    images = []
    for expr in faces:
        p = build_pose_prompt(spec, "front") + f", facial expression: {expr}"
        images.append((expr, engine._backend.render(
            prompt=p,
            width=engine.config.render.width // 2,
            height=engine.config.render.height // 2,
            seed=engine.config.render.seed,
        )))
    grid = compose_grid(images, columns=3)
    out = (out_dir or engine.config.output_dir) / f"{spec.slug}_expressions.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    grid.save(out)
    log.info("expression grid: %s (%d faces)", out, len(faces))
    return out


HANDLER = HandlerEntry(
    name="expression_grid",
    description="Render a 2xN facial expression sheet for a character.",
    run=run,
    order=20,
)