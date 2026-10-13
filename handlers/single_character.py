"""Handler: render one character from a prompt and write a turnaround sheet."""
from __future__ import annotations

import logging
from pathlib import Path

from handlers.registry import HandlerEntry
from models.character import CharacterSpec

log = logging.getLogger("turnaround.handlers.single")


def run(engine, *, prompt: str, out_dir: Path | str | None = None, **_ignored) -> object:
    out = Path(out_dir) if out_dir else engine.config.output_dir
    return engine.render_single(prompt=prompt, out_dir=out)


HANDLER = HandlerEntry(
    name="single_character",
    description="Render one character prompt to a turnaround sheet.",
    run=run,
    order=10,
)