"""號碼頻率 (Frequency) tab: bar chart + sortable table."""
from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import analysis
from ..models import Draw
from ..strings import s
from .widgets import NumericTableItem


class FrequencyTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        header = QLabel(s("freq_title"))
        header.setStyleSheet("font-size: 15px; font-weight: bold;")
        root.addWidget(header)
        root.addWidget(QLabel(s("freq_hot_hint")))

        body = QHBoxLayout()
        self.plot = pg.PlotWidget()
        self.plot.setBackground(None)
        self.plot.setMenuEnabled(False)
        self.plot.getAxis("bottom").setLabel(s("freq_col_number"))
        self.plot.getAxis("left").setLabel(s("freq_col_count"))
        body.addWidget(self.plot, 2)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            [s("freq_col_number"), s("freq_col_count"), s("freq_col_pct")]
        )
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        body.addWidget(self.table, 1)
        root.addLayout(body, 1)

    def set_data(self, draws: list[Draw], params: dict) -> None:
        include_extra = params.get("include_extra", False)
        rows = analysis.frequency_table(draws, include_extra)
        hot = {r["number"] for r in rows[:10]}
        cold = {r["number"] for r in rows[-10:]}

        # bar chart, ordered by number 1..59
        self.plot.clear()
        by_num = {r["number"]: r["count"] for r in rows}
        xs = sorted(by_num)
        ys = [by_num[n] for n in xs]
        brushes = [
            QColor("#d32f2f") if n in hot else
            (QColor("#1565c0") if n in cold else QColor("#9e9e9e"))
            for n in xs
        ]
        bars = pg.BarGraphItem(x=xs, height=ys, width=0.8, brushes=brushes)
        self.plot.addItem(bars)

        # table
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            num_item = NumericTableItem(r["number"])
            if r["number"] in hot:
                num_item.setForeground(QColor("#d32f2f"))
            elif r["number"] in cold:
                num_item.setForeground(QColor("#1565c0"))
            self.table.setItem(i, 0, num_item)
            self.table.setItem(i, 1, NumericTableItem(r["count"]))
            self.table.setItem(
                i, 2, NumericTableItem(r["pct"], f"{r['pct']:.1f}%")
            )
        self.table.setSortingEnabled(True)
