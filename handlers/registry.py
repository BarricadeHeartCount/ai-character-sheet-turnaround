"""Handler discovery + protocol.

A Handler is a small object with a name, a `run(engine, **kwargs)` callable,
and metadata the GUI uses to build a menu entry. Handlers are registered by
importing the package; `discover_handlers` walks submodules.
"""
from __future__ import annotations

import importlib
import logging
import pkgutil
from dataclasses import dataclass
from typing import Callable, Protocol

from config.schema import AppConfig

log = logging.getLogger("turnaround.handlers")


class Handler(Protocol):
    name: str
    description: str

    def run(self, engine, **kwargs) -> object: ...


@dataclass(frozen=True)
class HandlerEntry:
    name: str
    description: str
    run: Callable[..., object]
    order: int = 100


def discover_handlers(config: AppConfig) -> list[HandlerEntry]:
    """Import every submodule in `handlers/` and collect HandlerEntry objects.

    A module opts in by defining a module-level `HANDLER: HandlerEntry`.
    """
    import handlers as pkg

    found: list[HandlerEntry] = []
    for mod_info in pkgutil.iter_modules(pkg.__path__):
        if mod_info.name.startswith("_") or mod_info.name == "registry":
            continue
        try:
            module = importlib.import_module(f"handlers.{mod_info.name}")
        except Exception as exc:  # noqa: BLE001 — a broken handler must not kill startup
            log.warning("handler %s failed to import: %s", mod_info.name, exc)
            continue
        entry = getattr(module, "HANDLER", None)
        if entry is not None:
            found.append(entry)
    found.sort(key=lambda e: e.order)
    log.debug("handlers: %s", [e.name for e in found])
    return found