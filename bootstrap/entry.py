"""Primary entry point for the ai-character-sheet-turnaround desktop app.

Parses CLI flags, initializes logging, loads config, then hands off to the
Qt application shell. In `--dev` mode the config watcher stays hot and the
first-run wizard is skipped.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from config.loader import load_config
from core.engine import TurnaroundEngine
from handlers.registry import discover_handlers
from utils.logging_setup import configure_logging
from utils.paths import project_root


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ai-character-sheet-turnaround",
        description="Generate standardized character turnaround sheets from a prompt.",
    )
    parser.add_argument("--dev", action="store_true", help="Enable dev mode (hot config, verbose logs).")
    parser.add_argument("--config", type=Path, default=None, help="Override path to config.toml.")
    parser.add_argument("--prompt", type=str, default=None, help="Batch mode: render a single prompt and exit.")
    parser.add_argument("--out", type=Path, default=None, help="Batch mode: output directory.")
    parser.add_argument("--no-gui", action="store_true", help="Force headless batch mode.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    configure_logging(verbose=args.dev)
    log = logging.getLogger("turnaround.bootstrap")

    config_path = args.config or (project_root() / "config" / "default.toml")
    config = load_config(config_path)
    log.info("config loaded from %s (version=%s)", config_path, config.version)

    handlers = discover_handlers(config)
    log.info("discovered %d handlers: %s", len(handlers), [h.name for h in handlers])

    engine = TurnaroundEngine(config=config, handlers=handlers)

    if args.prompt or args.no_gui:
        if not args.prompt:
            log.error("--no-gui requires --prompt")
            return 2
        out_dir = args.out or (project_root() / "outputs")
        sheet = engine.render_single(prompt=args.prompt, out_dir=out_dir)
        log.info("wrote sheet: %s", sheet.path)
        return 0

    # Imported lazily so headless batch mode doesn't require Qt.
    from bootstrap.gui_shell import launch_gui

    return launch_gui(engine=engine, dev_mode=args.dev)


if __name__ == "__main__":
    raise SystemExit(main())