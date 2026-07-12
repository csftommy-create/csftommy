"""Global dark theme: palette, QSS stylesheet, and chart configuration.

Implements the v2.0 design language — near-black surfaces, orange accent,
condensed numerals. Call :func:`apply_theme` once on the QApplication before
building any widgets (pyqtgraph reads its config at widget-creation time).
"""
from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPalette

from ..config import THEME as T

# Font stack: condensed latin numerals + Traditional Chinese, with fallbacks
# that exist on Windows/macOS so we never depend on a bundled font.
FONT_STACK = "'Barlow Condensed', 'Microsoft JhengHei', 'PingFang TC', 'Noto Sans TC', sans-serif"
NUMERIC_FONT = QFont("Barlow Condensed")


def _qss() -> str:
    return f"""
    QWidget {{
        background: {T['bg']};
        color: {T['text']};
        font-family: {FONT_STACK};
        font-size: 13px;
    }}
    QMainWindow, QDialog {{ background: {T['bg']}; }}
    QToolTip {{
        background: {T['surface']}; color: {T['text']};
        border: 1px solid {T['surface_border']}; padding: 4px 6px;
    }}

    /* Tabs ---------------------------------------------------------------*/
    QTabWidget::pane {{
        border: 1px solid {T['panel_border']};
        border-radius: 12px; top: -1px; background: {T['bg']};
    }}
    QTabBar {{ qproperty-drawBase: 0; }}
    QTabBar::tab {{
        background: transparent; color: {T['text_muted']};
        padding: 8px 13px; margin-right: 3px;
        border: none; border-radius: 8px; font-size: 13px;
    }}
    QTabBar::tab:hover {{ color: {T['text']}; background: {T['surface']}; }}
    QTabBar::tab:selected {{
        color: {T['accent']}; background: {T['surface']};
        font-weight: 600;
    }}

    /* Buttons ------------------------------------------------------------*/
    QPushButton {{
        background: {T['surface']}; color: {T['text']};
        border: 1px solid {T['surface_border']}; border-radius: 8px;
        padding: 7px 16px;
    }}
    QPushButton:hover {{ border-color: {T['accent']}; color: {T['text']}; }}
    QPushButton:pressed {{ background: {T['surface_alt']}; }}
    QPushButton:disabled {{ color: {T['text_faint']}; border-color: {T['panel_border']}; }}
    QPushButton#accent {{
        background: {T['accent']}; color: #0A0A0B;
        border: none; font-weight: 700; padding: 9px 20px;
    }}
    QPushButton#accent:hover {{ background: {T['accent_hover']}; }}
    QPushButton#accent:pressed {{ background: {T['accent_press']}; }}

    /* Inputs -------------------------------------------------------------*/
    QComboBox, QSpinBox, QDateEdit, QLineEdit {{
        background: {T['surface']}; color: {T['text']};
        border: 1px solid {T['surface_border']}; border-radius: 7px;
        padding: 5px 8px; selection-background-color: {T['accent']};
        selection-color: #0A0A0B;
    }}
    QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QLineEdit:focus {{
        border-color: {T['accent']};
    }}
    QComboBox::drop-down, QDateEdit::drop-down {{ border: none; width: 18px; }}
    QComboBox QAbstractItemView {{
        background: {T['surface']}; color: {T['text']};
        border: 1px solid {T['surface_border']};
        selection-background-color: {T['accent']}; selection-color: #0A0A0B;
        outline: none;
    }}
    QSpinBox::up-button, QSpinBox::down-button {{ width: 16px; background: {T['surface_alt']}; }}

    /* Checkboxes ---------------------------------------------------------*/
    QCheckBox {{ color: {T['text_dim']}; spacing: 7px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px; border-radius: 4px;
        border: 1px solid {T['surface_border']}; background: {T['surface']};
    }}
    QCheckBox::indicator:checked {{
        background: {T['accent']}; border-color: {T['accent']};
    }}

    /* Group boxes --------------------------------------------------------*/
    QGroupBox {{
        background: {T['panel']}; border: 1px solid {T['panel_border']};
        border-radius: 12px; margin-top: 14px; padding: 10px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin; left: 12px; padding: 0 4px;
        color: {T['accent']}; font-weight: 600;
    }}

    /* Tables -------------------------------------------------------------*/
    QTableWidget, QTableView {{
        background: {T['panel']}; alternate-background-color: {T['surface_alt']};
        color: {T['text']}; gridline-color: {T['panel_border']};
        border: 1px solid {T['panel_border']}; border-radius: 10px;
        selection-background-color: {T['accent']}; selection-color: #0A0A0B;
        outline: none;
    }}
    QHeaderView::section {{
        background: {T['surface']}; color: {T['text_dim']};
        border: none; border-right: 1px solid {T['panel_border']};
        border-bottom: 1px solid {T['panel_border']}; padding: 6px 8px;
        font-weight: 600;
    }}
    QTableCornerButton::section {{ background: {T['surface']}; border: none; }}

    /* Scrollbars ---------------------------------------------------------*/
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: {T['surface_border']}; border-radius: 5px; min-height: 24px; }}
    QScrollBar::handle:vertical:hover {{ background: {T['text_faint']}; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
    QScrollBar::handle:horizontal {{ background: {T['surface_border']}; border-radius: 5px; min-width: 24px; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
    QScrollArea {{ border: none; }}

    /* Menu / toolbar / status -------------------------------------------*/
    QMenuBar {{ background: {T['bg']}; color: {T['text_dim']}; }}
    QMenuBar::item:selected {{ background: {T['surface']}; color: {T['text']}; }}
    QMenu {{ background: {T['surface']}; color: {T['text']}; border: 1px solid {T['surface_border']}; }}
    QMenu::item:selected {{ background: {T['accent']}; color: #0A0A0B; }}
    QToolBar {{ background: {T['bg']}; border: none; spacing: 4px; padding: 4px; }}
    QToolBar QToolButton {{ color: {T['text_dim']}; padding: 6px 12px; border-radius: 7px; }}
    QToolBar QToolButton:hover {{ background: {T['surface']}; color: {T['text']}; }}
    QStatusBar {{ background: {T['bg']}; color: {T['text_muted']}; border-top: 1px solid {T['panel_border']}; }}
    """


def apply_theme(app) -> None:
    """Apply the dark theme to the whole application."""
    app.setStyle("Fusion")

    # A dark base palette so native-drawn bits match the QSS.
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(T["bg"]))
    pal.setColor(QPalette.WindowText, QColor(T["text"]))
    pal.setColor(QPalette.Base, QColor(T["panel"]))
    pal.setColor(QPalette.AlternateBase, QColor(T["surface_alt"]))
    pal.setColor(QPalette.Text, QColor(T["text"]))
    pal.setColor(QPalette.Button, QColor(T["surface"]))
    pal.setColor(QPalette.ButtonText, QColor(T["text"]))
    pal.setColor(QPalette.Highlight, QColor(T["accent"]))
    pal.setColor(QPalette.HighlightedText, QColor(T["bg"]))
    pal.setColor(QPalette.ToolTipBase, QColor(T["surface"]))
    pal.setColor(QPalette.ToolTipText, QColor(T["text"]))
    pal.setColor(QPalette.PlaceholderText, QColor(T["text_faint"]))
    app.setPalette(pal)

    base = QFont()
    base.setPointSize(10)
    app.setFont(base)

    app.setStyleSheet(_qss())

    # pyqtgraph: transparent plot backgrounds show the panel; light foreground.
    try:
        import pyqtgraph as pg

        pg.setConfigOption("background", None)
        pg.setConfigOption("foreground", T["text_dim"])
        pg.setConfigOption("antialias", True)
    except Exception:
        pass
