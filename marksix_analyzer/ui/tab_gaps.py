"""遺漏分析 (Gaps) tab: heat grid + sortable table with gap heat coloring."""
from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QLabel,
    QSplitter,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from .. import analysis
from ..config import THEME as T
from ..models import Draw
from ..strings import s
from .widgets import NumberHeatGrid, NumericTableItem


class GapsTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)

        title = QLabel(s("gap_heading"))
        title.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {T['text']};"
        )
        root.addWidget(title)
        hint = QLabel(s("gap_hint") + "　·　" + s("gap_hint2"))
        hint.setStyleSheet(f"color: {T['text_muted']};")
        root.addWidget(hint)

        splitter = QSplitter(Qt.Horizontal)

        # Left: signature heat grid
        grid_wrap = QWidget()
        gl = QVBoxLayout(grid_wrap)
        gl.setContentsMargins(0, 0, 0, 0)
        self.heat = NumberHeatGrid()
        gl.addWidget(self.heat)
        gl.addStretch(1)
        splitter.addWidget(grid_wrap)

        # Right: detailed sortable table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            s("gap_col_number"), s("gap_col_current"),
            s("gap_col_max"), s("gap_col_avg"), s("gap_col_last"),
        ])
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        splitter.addWidget(self.table)
        splitter.setSizes([440, 520])
        root.addWidget(splitter, 1)

    def set_data(self, draws: list[Draw], params: dict) -> None:
        rows = analysis.gap_table(draws)
        max_gap = max((r["current_gap"] for r in rows), default=1) or 1

        # heat grid
        self.heat.set_values({r["number"]: r["current_gap"] for r in rows})

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, NumericTableItem(r["number"]))
            cur = NumericTableItem(r["current_gap"])
            # orange glow proportional to gap length (dark-theme friendly)
            intensity = min(1.0, r["current_gap"] / max_gap)
            cur.setBackground(QColor(255, 107, 26, int(40 + 150 * intensity)))
            if r["over_average"]:
                cur.setForeground(QColor(T["accent"]))
            self.table.setItem(i, 1, cur)
            self.table.setItem(i, 2, NumericTableItem(r["max_gap"]))
            self.table.setItem(
                i, 3, NumericTableItem(r["avg_gap"], f"{r['avg_gap']:.1f}")
            )
            self.table.setItem(
                i, 4, NumericTableItem(0, r["last_date"] or "—")
            )
        self.table.setSortingEnabled(True)
