"""分佈統計 (Distribution) tab: sum histogram, odd/even, high/low, consecutive, tail."""
from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .. import analysis
from ..models import Draw
from ..strings import s


def _bar_plot(title: str) -> pg.PlotWidget:
    p = pg.PlotWidget(title=title)
    p.setBackground(None)
    p.setMenuEnabled(False)
    return p


class DistributionTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        grid = QGridLayout()

        self.sum_plot = _bar_plot(s("dist_sum"))
        self.sum_stat = QLabel()
        self.oe_plot = _bar_plot(s("dist_oddeven"))
        self.hl_plot = _bar_plot(s("dist_highlow"))
        self.tail_plot = _bar_plot(s("tail_title"))

        grid.addWidget(self.sum_plot, 0, 0)
        grid.addWidget(self.oe_plot, 0, 1)
        grid.addWidget(self.hl_plot, 1, 0)
        grid.addWidget(self.tail_plot, 1, 1)
        root.addLayout(grid, 1)

        root.addWidget(self.sum_stat)
        self.consec_stat = QLabel()
        root.addWidget(self.consec_stat)
        self.tail_stat = QLabel()
        root.addWidget(self.tail_stat)

    def set_data(self, draws: list[Draw], params: dict) -> None:
        include_extra = params.get("include_extra", False)

        # sum histogram
        st = analysis.sum_stats(draws)
        self.sum_plot.clear()
        if st["histogram"]:
            xs = list(st["histogram"].keys())
            ys = list(st["histogram"].values())
            self.sum_plot.addItem(
                pg.BarGraphItem(x=xs, height=ys, width=1.0, brush="#1565c0")
            )
        self.sum_stat.setText(
            s("dist_sum_stat", mean=st["mean"], median=st["median"],
              std=st["std"])
        )

        # odd/even
        self._category_bars(self.oe_plot, analysis.odd_even_distribution(draws),
                            "#2e7d32")
        # high/low
        self._category_bars(self.hl_plot, analysis.high_low_distribution(draws),
                            "#d32f2f")

        # tail digit
        self.tail_plot.clear()
        tail = analysis.tail_frequency(draws, include_extra)
        self.tail_plot.addItem(
            pg.BarGraphItem(x=list(tail.keys()), height=list(tail.values()),
                            width=0.8, brush="#6a1b9a")
        )

        # text stats
        cs = analysis.consecutive_stats(draws)
        self.consec_stat.setText(s("dist_consecutive_stat", pct=cs["pct"]))
        ts = analysis.same_tail_stats(draws)
        self.tail_stat.setText(s("tail_same_stat", pct=ts["pct"]))

    @staticmethod
    def _category_bars(plot: pg.PlotWidget, dist: dict[str, int], color: str) -> None:
        plot.clear()
        labels = list(dist.keys())
        xs = list(range(len(labels)))
        ys = [dist[k] for k in labels]
        plot.addItem(pg.BarGraphItem(x=xs, height=ys, width=0.7, brush=color))
        ax = plot.getAxis("bottom")
        ax.setTicks([list(zip(xs, labels))])
