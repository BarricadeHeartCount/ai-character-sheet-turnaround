"""Qt application shell. Thin — all rendering logic lives in core/."""
from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from core.engine import TurnaroundEngine
from handlers.registry import Handler

log = logging.getLogger("turnaround.gui")


def launch_gui(engine: TurnaroundEngine, dev_mode: bool = False) -> int:
    """Boot the Qt event loop and open the main window.

    Args:
        engine: A fully constructed TurnaroundEngine.
        dev_mode: If True, enables the developer panel and hot-reloads handlers.

    Returns:
        Process exit code.
    """
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("ai-character-sheet-turnaround")
    app.setOrganizationName("turnaround-crew")

    # Deferred import: the window module pulls in heavy Qt widgets.
    from bootstrap.main_window import MainWindow

    window = MainWindow(engine=engine, dev_mode=dev_mode)
    window.show()
    log.info("main window shown (dev_mode=%s)", dev_mode)
    return app.exec()