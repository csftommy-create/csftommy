"""智能選號 (Smart Pick) tab: filters + generator + results + disclaimer."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .. import smart_pick
from ..db import Database
from ..models import Draw, Pick
from ..smart_pick import FilterConfig
from ..strings import s
from .widgets import BallRow, DisclaimerLabel


class SmartPickTab(QWidget):
    def __init__(self, db: Database, parent: QWidget | None = None):
        super().__init__(parent)
        self.db = db
        self._draws: list[Draw] = []
        self.saved = None  # optional callback set by main window

        root = QHBoxLayout(self)

        # ---- Left: filter panel -----------------------------------------
        filters = QGroupBox(s("sp_filters"))
        fl = QVBoxLayout(filters)
        self.cb_oddeven = QCheckBox(s("sp_filter_oddeven")); self.cb_oddeven.setChecked(True)
        self.cb_highlow = QCheckBox(s("sp_filter_highlow")); self.cb_highlow.setChecked(True)
        self.cb_consec = QCheckBox(s("sp_filter_consecutive")); self.cb_consec.setChecked(True)
        self.cb_sametail = QCheckBox(s("sp_filter_sametail")); self.cb_sametail.setChecked(True)
        self.cb_birthday = QCheckBox(s("sp_filter_birthday")); self.cb_birthday.setChecked(True)
        self.cb_arith = QCheckBox(s("sp_filter_arithmetic")); self.cb_arith.setChecked(True)
        self.cb_exclude = QCheckBox(s("sp_filter_exclude_last")); self.cb_exclude.setChecked(False)

        for cb in (self.cb_oddeven, self.cb_highlow):
            fl.addWidget(cb)

        # sum range row
        self.cb_sum = QCheckBox(s("sp_filter_sum")); self.cb_sum.setChecked(True)
        fl.addWidget(self.cb_sum)
        sum_row = QHBoxLayout()
        sum_row.addWidget(QLabel(s("sp_filter_sum_min")))
        self.sum_min = QSpinBox(); self.sum_min.setRange(21, 279); self.sum_min.setValue(100)
        sum_row.addWidget(self.sum_min)
        sum_row.addWidget(QLabel(s("sp_filter_sum_max")))
        self.sum_max = QSpinBox(); self.sum_max.setRange(21, 279); self.sum_max.setValue(200)
        sum_row.addWidget(self.sum_max)
        sum_row.addStretch(1)
        fl.addLayout(sum_row)

        for cb in (self.cb_consec, self.cb_sametail, self.cb_birthday,
                   self.cb_arith, self.cb_exclude):
            fl.addWidget(cb)

        # count + generate
        gen_row = QHBoxLayout()
        gen_row.addWidget(QLabel(s("sp_count_label")))
        self.count_spin = QSpinBox(); self.count_spin.setRange(1, 10); self.count_spin.setValue(3)
        gen_row.addWidget(self.count_spin)
        gen_row.addStretch(1)
        fl.addLayout(gen_row)
        self.generate_btn = QPushButton(s("sp_generate"))
        self.generate_btn.setObjectName("accent")
        self.generate_btn.clicked.connect(self._on_generate)
        fl.addWidget(self.generate_btn)
        fl.addStretch(1)
        root.addWidget(filters, 0)

        # ---- Right: results + disclaimer --------------------------------
        right = QVBoxLayout()
        right.addWidget(QLabel(f"<b>{s('sp_title')}</b>"))
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.addStretch(1)
        self.results_area.setWidget(self.results_container)
        right.addWidget(self.results_area, 1)
        right.addWidget(DisclaimerLabel(s("sp_disclaimer")))
        root.addLayout(right, 1)

    def set_data(self, draws: list[Draw], params: dict) -> None:
        self._draws = draws

    def _config(self) -> FilterConfig:
        last_nums = list(self._draws[-1].numbers) if self._draws else []
        return FilterConfig(
            odd_even=self.cb_oddeven.isChecked(),
            high_low=self.cb_highlow.isChecked(),
            sum_range=self.cb_sum.isChecked(),
            sum_min=self.sum_min.value(),
            sum_max=self.sum_max.value(),
            consecutive=self.cb_consec.isChecked(),
            same_tail=self.cb_sametail.isChecked(),
            birthday=self.cb_birthday.isChecked(),
            arithmetic=self.cb_arith.isChecked(),
            exclude_last=self.cb_exclude.isChecked(),
            last_draw_numbers=last_nums,
        )

    def _on_generate(self) -> None:
        cfg = self._config()
        count = self.count_spin.value()
        combos = smart_pick.generate(cfg, count=count)
        self._clear_results()
        if not combos:
            QMessageBox.warning(self, s("info"), s("sp_gen_failed"))
            return
        for combo in combos:
            self.results_layout.insertWidget(
                self.results_layout.count() - 1, self._make_result(combo)
            )

    def _clear_results(self) -> None:
        while self.results_layout.count() > 1:
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _make_result(self, combo: list[int]) -> QWidget:
        row = QWidget()
        lay = QHBoxLayout(row)
        lay.addWidget(BallRow(combo, diameter=36), 1)
        save_btn = QPushButton(s("save"))
        copy_btn = QPushButton(s("copy"))
        save_btn.clicked.connect(lambda: self._save(combo))
        copy_btn.clicked.connect(lambda: self._copy(combo))
        lay.addWidget(save_btn)
        lay.addWidget(copy_btn)
        return row

    def _save(self, combo: list[int]) -> None:
        self.db.save_pick(Pick(numbers=combo, method="smart"))
        if callable(self.saved):
            self.saved()
        QMessageBox.information(self, s("info"), s("sp_saved_ok"))

    def _copy(self, combo: list[int]) -> None:
        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(", ".join(str(n) for n in combo))
        QMessageBox.information(self, s("info"), s("sp_copied"))
