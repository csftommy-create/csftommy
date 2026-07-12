"""QThread workers for network fetch. UI never blocks on I/O."""
from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal

from .data_provider import DataProvider
from .models import Draw


class FetchWorker(QObject):
    """Runs a DataProvider fetch off the UI thread."""

    finished = Signal(list)   # list[Draw]
    failed = Signal(str)      # error message

    def __init__(self, provider: DataProvider, since_draw_id: str | None):
        super().__init__()
        self._provider = provider
        self._since = since_draw_id

    def run(self) -> None:
        try:
            draws: list[Draw] = self._provider.fetch_latest(self._since)
            self.finished.emit(draws)
        except Exception as exc:  # provider should already be defensive
            self.failed.emit(str(exc))


class FetchController(QObject):
    """Owns a worker + thread pair, exposing simple start()/signals.

    Keep a reference to this object on the calling widget so it is not
    garbage-collected while the thread runs.
    """

    finished = Signal(list)
    failed = Signal(str)

    def __init__(self, provider: DataProvider, since_draw_id: str | None,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._thread = QThread()
        self._worker = FetchWorker(provider, since_draw_id)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)

    def start(self) -> None:
        self._thread.start()

    def _cleanup(self) -> None:
        self._thread.quit()
        self._thread.wait()

    def _on_finished(self, draws: list) -> None:
        self._cleanup()
        self.finished.emit(draws)

    def _on_failed(self, msg: str) -> None:
        self._cleanup()
        self.failed.emit(msg)
