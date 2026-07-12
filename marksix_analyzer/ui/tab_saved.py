"""我的號碼 (Saved Picks) tab: list + 對獎 (prize checking)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import smart_pick
from ..db import Database
from ..models import Draw, Pick
from ..strings import s
from .widgets import BallRow


def _method_label(method: str) -> str:
    return {
        "smart": s("saved_method_smart"),
        "random": s("saved_method_random"),
        "manual": s("saved_method_manual"),
    }.get(method, method)


class CheckDialog(QDialog):
    """對獎: check one pick against a chosen historical draw."""

    def __init__(self, pick: Pick, draws: list[Draw], parent=None):
        super().__init__(parent)
        self.setWindowTitle(s("saved_check_title"))
        self._pick = pick
        self._draws = draws
        lay = QVBoxLayout(self)

        lay.addWidget(QLabel(s("saved_check_pick")))
        lay.addWidget(BallRow(pick.numbers, diameter=34))

        row = QHBoxLayout()
        row.addWidget(QLabel(s("saved_check_against")))
        self.combo = QComboBox()
        for d in reversed(draws):  # latest first
            self.combo.addItem(f"{d.draw_id}  {d.draw_date}", d)
        row.addWidget(self.combo, 1)
        lay.addLayout(row)

        self.draw_row = BallRow(diameter=30)
        lay.addWidget(self.draw_row)

        self.result_label = QLabel()
        self.result_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        lay.addWidget(self.result_label)
        self.detail_label = QLabel()
        lay.addWidget(self.detail_label)

        self.combo.currentIndexChanged.connect(self._update)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        lay.addWidget(buttons)

        if draws:
            self._update()

    def _update(self) -> None:
        draw = self.combo.currentData()
        if draw is None:
            return
        self.draw_row.set_numbers(list(draw.numbers), draw.extra)
        res = smart_pick.check_pick(self._pick.numbers, draw)
        if res["tier"]:
            self.result_label.setText(
                s("saved_check_result", tier=s(res["tier"]))
            )
            self.result_label.setStyleSheet(
                "font-size: 15px; font-weight: bold; color: #c62828;")
        else:
            self.result_label.setText(s("saved_check_none"))
            self.result_label.setStyleSheet(
                "font-size: 15px; font-weight: bold; color: palette(mid);")
        mains = "、".join(map(str, res["main_matches"])) or "—"
        extra = s("yes") if res["extra_matched"] else s("no")
        self.detail_label.setText(
            s("saved_check_matches", mains=mains, extra=extra)
        )


class SavedTab(QWidget):
    def __init__(self, db: Database, parent: QWidget | None = None):
        super().__init__(parent)
        self.db = db
        self._draws: list[Draw] = []
        root = QVBoxLayout(self)

        self.empty_label = QLabel(s("saved_empty"))
        self.empty_label.setStyleSheet("color: palette(mid);")
        root.addWidget(self.empty_label)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            s("saved_col_created"), s("saved_col_numbers"),
            s("saved_col_method"), s("saved_col_note"),
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table, 1)

        btns = QHBoxLayout()
        self.check_btn = QPushButton(s("saved_check"))
        self.delete_btn = QPushButton(s("saved_delete"))
        self.check_btn.clicked.connect(self._on_check)
        self.delete_btn.clicked.connect(self._on_delete)
        btns.addStretch(1)
        btns.addWidget(self.check_btn)
        btns.addWidget(self.delete_btn)
        root.addLayout(btns)

        self.reload()

    def set_data(self, draws: list[Draw], params: dict) -> None:
        self._draws = draws

    def reload(self) -> None:
        picks = self.db.all_picks()
        self.empty_label.setVisible(not picks)
        self.table.setRowCount(len(picks))
        for i, p in enumerate(picks):
            created = QTableWidgetItem(p.created_at or "")
            created.setData(Qt.UserRole, p.id)
            self.table.setItem(i, 0, created)
            self.table.setItem(
                i, 1, QTableWidgetItem(", ".join(map(str, p.numbers)))
            )
            self.table.setItem(
                i, 2, QTableWidgetItem(_method_label(p.method))
            )
            self.table.setItem(i, 3, QTableWidgetItem(p.note or ""))
        self.table.resizeColumnsToContents()

    def _selected_pick(self) -> Pick | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        pid = item.data(Qt.UserRole)
        for p in self.db.all_picks():
            if p.id == pid:
                return p
        return None

    def _on_check(self) -> None:
        pick = self._selected_pick()
        if pick is None:
            QMessageBox.information(self, s("info"), s("saved_empty"))
            return
        if not self._draws:
            QMessageBox.information(self, s("info"), s("status_no_data"))
            return
        CheckDialog(pick, self._draws, self).exec()

    def _on_delete(self) -> None:
        pick = self._selected_pick()
        if pick is None:
            return
        if QMessageBox.question(self, s("confirm_delete"), s("confirm_delete")) \
                == QMessageBox.Yes:
            self.db.delete_pick(pick.id)
            self.reload()
