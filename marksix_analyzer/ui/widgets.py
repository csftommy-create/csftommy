"""Reusable widgets: NumberBall, StatCard, FilterBar, disclaimer label."""
from __future__ import annotations

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QSizePolicy,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class NumericTableItem(QTableWidgetItem):
    """Table item that sorts by a numeric key but shows arbitrary text."""

    def __init__(self, value: float, text: str | None = None):
        super().__init__(text if text is not None else str(value))
        self._value = value
        self.setTextAlignment(Qt.AlignCenter)

    def __lt__(self, other) -> bool:  # noqa: D401 (Qt sort hook)
        if isinstance(other, NumericTableItem):
            return self._value < other._value
        return super().__lt__(other)


from ..config import THEME as T
from ..config import ball_color_hex
from ..strings import s


class NumberBall(QWidget):
    """A custom-painted circular number ball, colored per HKJC mapping."""

    def __init__(self, number: int, diameter: int = 40, extra: bool = False,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self._number = number
        self._diameter = diameter
        self._extra = extra
        self.setFixedSize(diameter, diameter)
        self.setToolTip(
            f"{number}（{s('dash_extra_label')}）" if extra else str(number)
        )

    def set_number(self, number: int, extra: bool = False) -> None:
        self._number = number
        self._extra = extra
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        color = QColor(ball_color_hex(self._number))
        d = self._diameter
        if self._extra:
            pen = p.pen()
            pen.setColor(QColor(T["accent"]))
            pen.setWidth(3)
            p.setPen(pen)
        else:
            p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawEllipse(1, 1, d - 2, d - 2)
        # subtle top highlight for a glossy, on-dark look
        gloss = QColor(255, 255, 255, 40)
        p.setPen(Qt.NoPen)
        p.setBrush(gloss)
        p.drawEllipse(int(d * 0.22), int(d * 0.12), int(d * 0.56), int(d * 0.4))
        p.setPen(QColor("white"))
        font = QFont("Barlow Condensed")
        font.setBold(True)
        font.setPointSize(max(9, int(d / 2.6)))
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignCenter, str(self._number))
        p.end()


class BallRow(QWidget):
    """A horizontal row of NumberBalls (6 main + optional extra)."""

    def __init__(self, numbers: list[int] | None = None, extra: int | None = None,
                 diameter: int = 40, parent: QWidget | None = None):
        super().__init__(parent)
        self._diameter = diameter
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        self._layout.addStretch(0)
        if numbers is not None:
            self.set_numbers(numbers, extra)

    def set_numbers(self, numbers: list[int], extra: int | None = None) -> None:
        # clear
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for n in sorted(numbers):
            self._layout.addWidget(NumberBall(n, self._diameter))
        if extra is not None:
            sep = QLabel("＋")
            sep.setAlignment(Qt.AlignCenter)
            self._layout.addWidget(sep)
            self._layout.addWidget(NumberBall(extra, self._diameter, extra=True))
        self._layout.addStretch(1)


class StatCard(QFrame):
    """A titled stat card for the dashboard (dark panel, accent value)."""

    def __init__(self, title: str, accent: bool = False,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setStyleSheet(
            f"#statCard {{ border: 1px solid {T['panel_border']};"
            f" border-radius: 12px; background: {T['panel']}; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        self._title = QLabel(title)
        self._title.setStyleSheet(
            f"color: {T['text_muted']}; font-size: 12px; "
            "font-weight: 600; letter-spacing: 1px; background: transparent;"
        )
        self._value = QLabel("—")
        value_color = T["accent"] if accent else T["text"]
        self._value.setStyleSheet(
            f"color: {value_color}; font-size: 22px; font-weight: 700; "
            "background: transparent;"
        )
        self._value.setWordWrap(True)
        lay.addWidget(self._title)
        lay.addWidget(self._value)
        lay.addStretch(1)

    def set_value(self, text: str) -> None:
        self._value.setText(text)


class DisclaimerLabel(QLabel):
    """Non-dismissible mandatory disclaimer banner (dark amber)."""

    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setStyleSheet(
            f"background: {T['warn_bg']}; color: {T['warn_text']}; "
            f"border: 1px solid {T['warn_border']}; border-radius: 8px; "
            "padding: 9px 12px; font-size: 12px;"
        )
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)


class FilterBar(QWidget):
    """Global range filter: 全部 / 最近 50 / 最近 100 / 自訂範圍 (+ include extra)."""

    changed = Signal()

    MODE_ALL = 0
    MODE_LAST50 = 1
    MODE_LAST100 = 2
    MODE_CUSTOM = 3

    def __init__(self, show_extra_toggle: bool = True,
                 parent: QWidget | None = None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(QLabel(s("filter_label")))

        self.combo = QComboBox()
        self.combo.addItems([
            s("filter_all"), s("filter_last50"),
            s("filter_last100"), s("filter_custom"),
        ])
        self.combo.currentIndexChanged.connect(self._on_mode)
        lay.addWidget(self.combo)

        self.from_edit = QDateEdit()
        self.from_edit.setCalendarPopup(True)
        self.from_edit.setDisplayFormat("yyyy-MM-dd")
        self.from_edit.setDate(QDate.currentDate().addYears(-1))
        self.to_edit = QDateEdit()
        self.to_edit.setCalendarPopup(True)
        self.to_edit.setDisplayFormat("yyyy-MM-dd")
        self.to_edit.setDate(QDate.currentDate())
        self._from_label = QLabel(s("filter_from"))
        self._to_label = QLabel(s("filter_to"))
        for w in (self._from_label, self.from_edit, self._to_label, self.to_edit):
            lay.addWidget(w)
            w.setVisible(False)
        self.from_edit.dateChanged.connect(lambda *_: self.changed.emit())
        self.to_edit.dateChanged.connect(lambda *_: self.changed.emit())

        self.include_extra = QCheckBox(s("filter_include_extra"))
        self.include_extra.stateChanged.connect(lambda *_: self.changed.emit())
        if show_extra_toggle:
            lay.addWidget(self.include_extra)
        else:
            self.include_extra.setVisible(False)

        lay.addStretch(1)

    def _on_mode(self, idx: int) -> None:
        custom = idx == self.MODE_CUSTOM
        for w in (self._from_label, self.from_edit, self._to_label, self.to_edit):
            w.setVisible(custom)
        self.changed.emit()

    def params(self) -> dict:
        """Return {last_n, date_from, date_to, include_extra}."""
        idx = self.combo.currentIndex()
        last_n = None
        date_from = date_to = None
        if idx == self.MODE_LAST50:
            last_n = 50
        elif idx == self.MODE_LAST100:
            last_n = 100
        elif idx == self.MODE_CUSTOM:
            date_from = self.from_edit.date().toString("yyyy-MM-dd")
            date_to = self.to_edit.date().toString("yyyy-MM-dd")
        return {
            "last_n": last_n,
            "date_from": date_from,
            "date_to": date_to,
            "include_extra": self.include_extra.isChecked(),
        }


class BrandBadge(QWidget):
    """Orange rounded-square badge with the 「六」 glyph."""

    def __init__(self, size: int = 34, parent: QWidget | None = None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(T["accent"]))
        r = self._size
        p.drawRoundedRect(0, 0, r, r, r * 0.28, r * 0.28)
        p.setPen(QColor(T["bg"]))
        font = QFont()
        font.setBold(True)
        font.setPointSize(int(r / 2.2))
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignCenter, "六")
        p.end()


class BrandHeader(QWidget):
    """Top brand bar: badge + title + version, latest-draw pill, language toggle.

    ``lang_button`` is exposed so the main window can connect the toggle.
    """

    def __init__(self, title: str, subtitle: str, lang_label: str,
                 parent: QWidget | None = None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 2, 4, 6)
        lay.setSpacing(10)
        lay.addWidget(BrandBadge(34))

        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        self._title = QLabel(title)
        self._title.setStyleSheet(
            f"color: {T['text']}; font-size: 17px; font-weight: 700; "
            "background: transparent;"
        )
        self._sub = QLabel(subtitle)
        self._sub.setStyleSheet(
            f"color: {T['text_muted']}; font-size: 11px; background: transparent;"
        )
        text_col.addWidget(self._title)
        text_col.addWidget(self._sub)
        lay.addLayout(text_col)
        lay.addStretch(1)

        self.pill = QLabel("")
        self.pill.setStyleSheet(
            f"color: {T['text_dim']}; background: {T['surface']}; "
            f"border: 1px solid {T['surface_border']}; border-radius: 12px; "
            "padding: 5px 12px; font-size: 12px;"
        )
        lay.addWidget(self.pill)

        # Language toggle — text is the language it switches to (EN / 中文).
        self.lang_button = QPushButton(f"🌐 {lang_label}")
        self.lang_button.setCursor(Qt.PointingHandCursor)
        lay.addWidget(self.lang_button)

    def set_pill(self, text: str) -> None:
        self.pill.setText(text)


class NumberHeatGrid(QWidget):
    """A 1–49 grid whose cells glow orange in proportion to a per-number value.

    Signature component of the redesign's 遺漏 (gaps) screen: brighter cell =
    longer current gap. ``values`` maps number -> magnitude; the max is scaled
    to full accent intensity.
    """

    COLS = 7

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setSpacing(6)
        self._cells: dict[int, QLabel] = {}
        for n in range(1, 50):
            cell = QLabel()
            cell.setAlignment(Qt.AlignCenter)
            cell.setFixedHeight(46)
            cell.setMinimumWidth(46)
            self._cells[n] = cell
            row, col = divmod(n - 1, self.COLS)
            self._grid.addWidget(cell, row, col)

    def set_values(self, values: dict[int, float]) -> None:
        vmax = max(values.values(), default=0) or 1
        for n, cell in self._cells.items():
            v = values.get(n, 0)
            t = min(1.0, v / vmax)
            # rgba(255,107,26, 0.06..0.90) glow scaled by gap length
            alpha = 0.06 + t * 0.84
            border = T["accent"] if t > 0.66 else T["surface_border"]
            text_color = T["text"] if t > 0.4 else T["text_muted"]
            cell.setStyleSheet(
                f"background: rgba(255,107,26,{alpha:.2f}); "
                f"border: 1px solid {border}; border-radius: 8px; "
                f"color: {text_color}; background-clip: padding;"
            )
            cell.setText(
                f"<div style='font-size:15px;font-weight:700;color:{text_color}'>{n:02d}</div>"
                f"<div style='font-size:10px;color:{T['text_muted']}'>{int(v)}</div>"
            )
            cell.setToolTip(f"{n}：遺漏 {int(v)} 期")
