"""Entry point: QApplication setup + main window."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .config import APP_NAME_ZH, ensure_data_dir
from .db import Database
from .ui.main_window import MainWindow
from .ui.theme import apply_theme


def main() -> int:
    """Start the Mark Six Analyzer application."""
    ensure_data_dir()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME_ZH)
    apply_theme(app)

    db = Database()
    window = MainWindow(db)
    window.show()
    code = app.exec()
    db.close()
    return code


if __name__ == "__main__":
    sys.exit(main())
