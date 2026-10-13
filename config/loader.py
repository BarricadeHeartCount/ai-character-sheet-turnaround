"""TOML → AppConfig loader with version migration hooks."""
from __future__ import annotations

import logging
from pathlib import Path

import tomli

from config.schema import AppConfig, CONFIG_VERSION

log = logging.getLogger("turnaround.config")


def load_config(path: Path) -> AppConfig:
    """Load and validate a config.toml. Falls back to defaults if missing."""
    if not path.exists():
        log.warning("config not found at %s — using defaults", path)
        return AppConfig()

    with path.open("rb") as fh:
        raw = tomli.load(fh)

    on_disk_version = int(raw.get("version", 1))
    if on_disk_version != CONFIG_VERSION:
        log.warning(
            "config version mismatch: file=%d code=%d — applying best-effort migration",
            on_disk_version,
            CONFIG_VERSION,
        )
        raw = _migrate(raw, from_version=on_disk_version)

    return AppConfig.model_validate(raw)


def _migrate(raw: dict, from_version: int) -> dict:
    """Best-effort migration. Only forward-compatible keys survive."""
    out = dict(raw)
    if from_version < 3 and "sheet" in out:
        # v3 renamed `cols` to `grid_columns`.
        sheet = dict(out.get("sheet", {}))
        if "cols" in sheet:
            sheet["grid_columns"] = sheet.pop("cols")
        out["sheet"] = sheet
    out["version"] = CONFIG_VERSION
    return out