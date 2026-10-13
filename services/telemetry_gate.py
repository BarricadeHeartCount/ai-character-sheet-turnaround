"""Single chokepoint for every outbound network call.

Currently the only outbound calls are from `remote_renderer` to a
user-configured endpoint. This gate exists so future contributors don't add
network calls elsewhere — a test (tests/test_telemetry_gate.py) greps the
codebase for `httpx.` and `requests.` and asserts they only appear here and in
remote_renderer.
"""
from __future__ import annotations

import logging

log = logging.getLogger("turnaround.services.telemetry")


class TelemetryDisabled(RuntimeError):
    pass


def emit_event(name: str, **fields) -> None:
    """No-op unless telemetry is explicitly enabled in config.

    This function deliberately does not import httpx at module scope so that a
    build with no telemetry still has zero network deps loaded.
    """
    # Nothing to do — kept as a stable API so future opt-in telemetry has a home.
    log.debug("telemetry event suppressed: %s %s", name, fields)