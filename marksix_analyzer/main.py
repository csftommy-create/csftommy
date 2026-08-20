"""Entry point: QApplication setup + main window."""
from __future__ import annotations

import sys


def main() -> int:
    # Package-relative imports work whether run as a module or a frozen exe.
    from PySide6.QtWidgets import QApplication

    try:
        from .config import APP_NAME_ZH, ensure_data_dir
        from .db import Database
        from .ui.main_window import MainWindow
        from .ui.theme import apply_theme
    except ImportError:
        # Running as a plain script (python UKLottoAnalyzer/main.py)
        from UKLottoAnalyzer.config import APP_NAME_ZH, ensure_data_dir
        from UKLottoAnalyzer.db import Database
        from UKLottoAnalyzer.ui.main_window import MainWindow
        from UKLottoAnalyzer.ui.theme import apply_theme

    ensure_data_dir()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME_ZH)
    apply_theme(app)  # dark theme + chart config, before any widgets are built

    db = Database()
    window = MainWindow(db)
    window.show()
    code = app.exec()
    db.close()
    return code


if __name__ == "__main__":
    sys.exit(main())
