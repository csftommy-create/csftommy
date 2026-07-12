"""總覽 (Dashboard) tab."""
from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .. import analysis
from ..models import Draw
from ..strings import s
from .widgets import BallRow, DisclaimerLabel, StatCard


class DashboardTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)

        # Latest draw
        title = QLabel(s("dash_latest_draw"))
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        root.addWidget(title)

        self.date_label = QLabel("—")
        self.date_label.setStyleSheet("color: palette(mid);")
        root.addWidget(self.date_label)

        self.ball_row = BallRow(diameter=52)
        root.addWidget(self.ball_row)

        self.next_label = QLabel()
        root.addWidget(self.next_label)

        # Stat cards
        cards = QHBoxLayout()
        self.card_hot = StatCard(s("dash_hot"), accent=True)
        self.card_cold = StatCard(s("dash_cold"))
        self.card_gap = StatCard(s("dash_max_gap"))
        for c in (self.card_hot, self.card_cold, self.card_gap):
            cards.addWidget(c)
        root.addLayout(cards)

        # Mini frequency chart
        chart_label = QLabel(s("dash_mini_freq"))
        chart_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        root.addWidget(chart_label)
        self.plot = pg.PlotWidget()
        self.plot.setBackground(None)
        self.plot.setMenuEnabled(False)
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.getAxis("bottom").setLabel(s("freq_col_number"))
        root.addWidget(self.plot, 1)

        root.addWidget(DisclaimerLabel(s("disclaimer_body")))

    def set_data(self, draws: list[Draw], params: dict) -> None:
        latest = draws[-1] if draws else None
        if latest:
            self.ball_row.set_numbers(list(latest.numbers), latest.extra)
            self.date_label.setText(
                f"{s('data_col_draw')} {latest.draw_id}　{latest.draw_date}"
            )
        else:
            self.ball_row.set_numbers([])
            self.date_label.setText(s("status_no_data"))
        self.next_label.setText(
            f"{s('dash_next_draw')}：{s('dash_next_unknown')}"
        )

        # stat cards use the filtered window
        hot, cold = analysis.hot_cold(draws, top=5)
        self.card_hot.set_value("、".join(map(str, hot)) if hot else "—")
        self.card_cold.set_value("、".join(map(str, cold)) if cold else "—")
        gap_rows = analysis.gap_table(draws)
        if gap_rows:
            top = gap_rows[0]
            self.card_gap.set_value(
                f"{top['number']}（{top['current_gap']} 期）"
            )
        else:
            self.card_gap.set_value("—")

        # mini chart
        self.plot.clear()
        freq = analysis.frequency(draws)
        xs = list(freq.keys())
        ys = list(freq.values())
        bars = pg.BarGraphItem(x=xs, height=ys, width=0.8, brush="#FF6B1A")
        self.plot.addItem(bars)
