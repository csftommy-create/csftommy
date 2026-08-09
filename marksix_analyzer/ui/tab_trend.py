"""走勢圖 (Trend) tab: scatter of drawn numbers over recent draws."""
from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .. import analysis
from ..models import Draw
from ..strings import s


class TrendTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._draws: list[Draw] = []
        root = QVBoxLayout(self)

        controls = QHBoxLayout()
        controls.addWidget(QLabel(s("trend_count_label")))
        self.count_combo = QComboBox()
        for n in (30, 50, 80, 100):
            self.count_combo.addItem(f"{n}", n)
        self.count_combo.setCurrentText("50")
        self.count_combo.currentIndexChanged.connect(self._redraw)
        controls.addWidget(self.count_combo)
        controls.addStretch(1)
        root.addLayout(controls)

        self.plot = pg.PlotWidget(title=s("trend_title"))
        self.plot.setBackground(None)
        self.plot.setMenuEnabled(False)
        self.plot.getAxis("left").setLabel(s("gap_col_number"))
        self.plot.getAxis("bottom").setLabel(s("data_col_draw"))
        self.plot.setYRange(1, 59)
        root.addWidget(self.plot, 1)

    def set_data(self, draws: list[Draw], params: dict) -> None:
        self._draws = draws
        self._redraw()

    def _redraw(self) -> None:
        self.plot.clear()
        if not self._draws:
            return
        last_n = self.count_combo.currentData() or 50
        points = analysis.trend_points(self._draws, last_n)
        main_x = [p["x"] for p in points if not p["extra"]]
        main_y = [p["y"] for p in points if not p["extra"]]
        extra_x = [p["x"] for p in points if p["extra"]]
        extra_y = [p["y"] for p in points if p["extra"]]
        self.plot.addItem(pg.ScatterPlotItem(
            x=main_x, y=main_y, size=9, brush="#7E93AB", pen=None))
        self.plot.addItem(pg.ScatterPlotItem(
            x=extra_x, y=extra_y, size=10, brush="#FF6B1A",
            pen=pg.mkPen("#C93F00")))
