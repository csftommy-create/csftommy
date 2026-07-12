"""資料管理 (Data) tab: paginated history, import/export, manual entry, stats."""
from __future__ import annotations

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..db import Database
from ..models import Draw
from ..strings import s

PAGE_SIZE = 50


class ManualEntryDialog(QDialog):
    """Key in a single draw result by hand."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(s("manual_title"))
        form = QFormLayout(self)

        self.draw_id = QLineEdit()
        self.draw_id.setPlaceholderText("26/078")
        form.addRow(s("manual_draw_id"), self.draw_id)

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setDate(QDate.currentDate())
        form.addRow(s("manual_date"), self.date)

        self.spins: list[QSpinBox] = []
        num_row = QHBoxLayout()
        for _ in range(6):
            sp = QSpinBox()
            sp.setRange(1, 49)
            self.spins.append(sp)
            num_row.addWidget(sp)
        num_wrap = QWidget()
        num_wrap.setLayout(num_row)
        form.addRow(s("manual_numbers"), num_wrap)

        self.extra = QSpinBox()
        self.extra.setRange(1, 49)
        form.addRow(s("manual_extra"), self.extra)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
        self._draw: Draw | None = None

    def _on_accept(self) -> None:
        draw_id = self.draw_id.text().strip()
        if not draw_id:
            QMessageBox.warning(self, s("error"),
                                s("manual_invalid", reason=s("manual_draw_id")))
            return
        nums = [sp.value() for sp in self.spins]
        extra = self.extra.value()
        if len(set(nums)) != 6:
            QMessageBox.warning(self, s("error"),
                                s("manual_invalid", reason=s("manual_dup_number")))
            return
        if extra in nums:
            QMessageBox.warning(self, s("error"),
                                s("manual_invalid", reason=s("manual_dup_number")))
            return
        self._draw = Draw(
            draw_id=draw_id,
            draw_date=self.date.date().toString("yyyy-MM-dd"),
            numbers=tuple(sorted(nums)),
            extra=extra,
        )
        self.accept()

    def result_draw(self) -> Draw | None:
        return self._draw


class DataTab(QWidget):
    request_import = Signal()
    request_export = Signal()
    request_refresh = Signal()
    request_manual_add = Signal()

    def __init__(self, db: Database, parent: QWidget | None = None):
        super().__init__(parent)
        self.db = db
        self._page = 0
        root = QVBoxLayout(self)

        # stats + actions
        top = QHBoxLayout()
        self.stats_label = QLabel()
        top.addWidget(self.stats_label, 1)
        for text, sig in (
            (s("action_refresh"), self.request_refresh),
            (s("action_import_csv"), self.request_import),
            (s("action_export_csv"), self.request_export),
            (s("action_manual_add"), self.request_manual_add),
        ):
            btn = QPushButton(text)
            btn.clicked.connect(sig.emit)
            top.addWidget(btn)
        root.addLayout(top)

        # table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            s("data_col_draw"), s("data_col_date"), s("data_col_numbers"),
            s("data_col_extra"), s("data_col_jackpot"),
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table, 1)

        # pagination
        pager = QHBoxLayout()
        self.prev_btn = QPushButton(s("data_page_prev"))
        self.next_btn = QPushButton(s("data_page_next"))
        self.page_label = QLabel()
        self.prev_btn.clicked.connect(lambda: self._go(-1))
        self.next_btn.clicked.connect(lambda: self._go(1))
        pager.addStretch(1)
        pager.addWidget(self.prev_btn)
        pager.addWidget(self.page_label)
        pager.addWidget(self.next_btn)
        root.addLayout(pager)

        self.reload()

    def set_data(self, draws: list[Draw], params: dict) -> None:
        self.reload()

    def _total_pages(self) -> int:
        count = self.db.count_draws()
        return max(1, (count + PAGE_SIZE - 1) // PAGE_SIZE)

    def _go(self, delta: int) -> None:
        self._page = max(0, min(self._page + delta, self._total_pages() - 1))
        self.reload()

    def reload(self) -> None:
        count = self.db.count_draws()
        lo, hi = self.db.date_range()
        self.stats_label.setText(
            s("data_total", count=count) + "　" +
            (s("data_range", start=lo, end=hi) if lo else "")
        )
        total_pages = self._total_pages()
        self._page = min(self._page, total_pages - 1)
        rows = self.db.draws_page(self._page, PAGE_SIZE)
        self.table.setRowCount(len(rows))
        for i, d in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(d.draw_id))
            self.table.setItem(i, 1, QTableWidgetItem(d.draw_date))
            self.table.setItem(
                i, 2, QTableWidgetItem(" ".join(f"{n:02d}" for n in d.numbers))
            )
            self.table.setItem(i, 3, QTableWidgetItem(str(d.extra)))
            self.table.setItem(
                i, 4,
                QTableWidgetItem(str(d.jackpot) if d.jackpot is not None else "—"),
            )
        self.page_label.setText(
            s("data_page_info", page=self._page + 1, total=total_pages)
        )
        self.prev_btn.setEnabled(self._page > 0)
        self.next_btn.setEnabled(self._page < total_pages - 1)
