"""Main application window."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QThread
from PySide6.QtGui import QColor, QDragEnterEvent, QDropEvent, QIcon, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from pixicon import __version__
from pixicon.core.convert import source_pixel_size
from pixicon.core.formats import FILE_DIALOG_FILTER, is_supported
from pixicon.core.sizes import DEFAULT_TARGET_SIZE, TARGET_SIZES, size_label
from pixicon.gui.styles import APP_STYLESHEET
from pixicon.gui.workers import ConvertJob, ConvertResult, ConvertWorker
from pixicon.paths import asset_path


def _icon_path() -> Path:
    return asset_path("pixicon-app-icon.png")


def _format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def _open_path(path: Path) -> None:
    path = path.resolve()
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


class DropListWidget(QListWidget):
    """List that accepts dropped image files and shows an empty-state hint."""

    def __init__(self, on_paths, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._on_paths = on_paths
        self._placeholder = "Drag & drop files here"
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(False)
        self.setWordWrap(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:  # noqa: ANN001
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        paths: list[Path] = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                paths.append(Path(url.toLocalFile()))
        if paths:
            self._on_paths(paths)
            event.acceptProposedAction()
        else:
            event.ignore()

    def paintEvent(self, event) -> None:  # noqa: ANN001
        super().paintEvent(event)
        if self.count() > 0:
            return
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.viewport().rect().adjusted(12, 12, -12, -12)
        pen = QPen(QColor("#4a5568"))
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(QColor("#181e2a"))
        painter.drawRoundedRect(rect, 6, 6)
        painter.setPen(QColor("#7a8799"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._placeholder)
        painter.end()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Pixicon — Pixelated SVG Icon Converter (v{__version__})")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(APP_STYLESHEET)

        icon_file = _icon_path()
        if icon_file.is_file():
            self.setWindowIcon(QIcon(str(icon_file)))

        self._sources: list[Path] = []
        self._thread: QThread | None = None
        self._worker: ConvertWorker | None = None

        self._build_ui()
        self._append_log("Application started. Ready.")

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(12)
        root.addLayout(top, stretch=3)

        top.addWidget(self._build_source_panel(), stretch=5)
        top.addWidget(self._build_convert_button(), stretch=0, alignment=Qt.AlignVCenter)
        top.addWidget(self._build_target_panel(), stretch=5)

        root.addWidget(self._build_log_panel(), stretch=2)

    def _build_source_panel(self) -> QGroupBox:
        box = QGroupBox("Source Files")
        layout = QVBoxLayout(box)

        path_row = QHBoxLayout()
        self.source_path_edit = QLineEdit()
        self.source_path_edit.setPlaceholderText("Select image files…")
        self.source_path_edit.setReadOnly(True)
        browse_btn = QPushButton("…")
        browse_btn.setFixedWidth(40)
        browse_btn.setToolTip("Browse for image files")
        browse_btn.clicked.connect(self._browse_sources)
        path_row.addWidget(self.source_path_edit)
        path_row.addWidget(browse_btn)
        layout.addLayout(path_row)

        self.source_list = DropListWidget(self._add_sources)
        self.source_list.setObjectName("sourceList")
        layout.addWidget(self.source_list, stretch=1)

        btn_row = QHBoxLayout()
        remove_btn = QPushButton("Remove selected")
        remove_btn.clicked.connect(self._remove_selected_sources)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_sources)
        btn_row.addWidget(remove_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        return box

    def _build_convert_button(self) -> QWidget:
        wrap = QFrame()
        wrap.setFixedWidth(110)
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        self.convert_btn = QPushButton("⚡\nCONVERT")
        self.convert_btn.setObjectName("convertButton")
        self.convert_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.convert_btn.clicked.connect(self._start_conversion)
        layout.addStretch()
        layout.addWidget(self.convert_btn, alignment=Qt.AlignCenter)
        layout.addStretch()
        return wrap

    def _build_target_panel(self) -> QGroupBox:
        box = QGroupBox("Target Folder & Settings")
        layout = QVBoxLayout(box)

        path_row = QHBoxLayout()
        self.target_path_edit = QLineEdit()
        self.target_path_edit.setPlaceholderText("Select output folder…")
        browse_btn = QPushButton("…")
        browse_btn.setFixedWidth(40)
        browse_btn.setToolTip("Browse for output folder")
        browse_btn.clicked.connect(self._browse_target)
        path_row.addWidget(self.target_path_edit)
        path_row.addWidget(browse_btn)
        layout.addLayout(path_row)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Target size"))
        self.size_combo = QComboBox()
        for n in TARGET_SIZES:
            self.size_combo.addItem(size_label(n), n)
        self.size_combo.setCurrentIndex(TARGET_SIZES.index(DEFAULT_TARGET_SIZE))
        size_row.addWidget(self.size_combo, stretch=1)
        layout.addLayout(size_row)

        results_label = QLabel("Converted images (double-click or View to open)")
        results_label.setObjectName("hintLabel")
        layout.addWidget(results_label)

        self.results_list = QListWidget()
        self.results_list.setObjectName("resultsList")
        self.results_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.results_list.setUniformItemSizes(True)
        self.results_list.setSpacing(2)
        self.results_list.itemDoubleClicked.connect(self._view_result_item)
        layout.addWidget(self.results_list, stretch=1)

        view_btn = QPushButton("View selected")
        view_btn.clicked.connect(self._view_selected_result)
        layout.addWidget(view_btn)
        return box

    def _build_log_panel(self) -> QGroupBox:
        box = QGroupBox("Process Log")
        layout = QVBoxLayout(box)
        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("processLog")
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(2000)
        layout.addWidget(self.log_view)
        return box

    # --- sources ---

    def _browse_sources(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select image files",
            self.source_path_edit.text() or str(Path.home()),
            FILE_DIALOG_FILTER,
        )
        if paths:
            self._add_sources([Path(p) for p in paths])

    def _add_sources(self, paths: list[Path]) -> None:
        added = 0
        skipped = 0
        known = {p.resolve() for p in self._sources}
        for path in paths:
            path = path.expanduser()
            if not path.is_file():
                skipped += 1
                self._append_log(f"Skipped (not a file): {path}")
                continue
            if not is_supported(path):
                skipped += 1
                self._append_log(f"Skipped (unsupported type): {path.name}")
                continue
            resolved = path.resolve()
            if resolved in known:
                continue
            known.add(resolved)
            self._sources.append(path)
            added += 1
            item = QListWidgetItem(self._source_item_text(path))
            item.setSizeHint(QSize(0, 44))
            self.source_list.addItem(item)
            self.source_list.viewport().update()

        if self._sources:
            self.source_path_edit.setText(str(self._sources[-1]))
        if added:
            self._append_log(f"{added} file(s) added to the queue.")
        if skipped and not added:
            self._append_log("No valid files were added.")

    def _source_item_text(self, path: Path) -> str:
        try:
            size = path.stat().st_size
            w, h = source_pixel_size(path)
            meta = f"{w}x{h} | {_format_bytes(size)}"
        except Exception:
            meta = "unreadable"
        return f"{path.name}\n{meta}"

    def _remove_selected_sources(self) -> None:
        rows = sorted({i.row() for i in self.source_list.selectedIndexes()}, reverse=True)
        for row in rows:
            self.source_list.takeItem(row)
            del self._sources[row]
        if self._sources:
            self.source_path_edit.setText(str(self._sources[-1]))
        else:
            self.source_path_edit.clear()
        self.source_list.viewport().update()

    def _clear_sources(self) -> None:
        self._sources.clear()
        self.source_list.clear()
        self.source_path_edit.clear()
        self.source_list.viewport().update()

    # --- target ---

    def _browse_target(self) -> None:
        start = self.target_path_edit.text() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "Select output folder", start)
        if folder:
            self.target_path_edit.setText(folder)

    def _target_size(self) -> int:
        return int(self.size_combo.currentData())

    # --- convert ---

    def _start_conversion(self) -> None:
        if self._thread is not None:
            return
        if not self._sources:
            QMessageBox.information(self, "Pixicon", "Add at least one source image.")
            return
        target = self.target_path_edit.text().strip()
        if not target:
            QMessageBox.information(self, "Pixicon", "Choose a target folder.")
            return
        out_dir = Path(target).expanduser()
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(self, "Pixicon", f"Cannot create target folder:\n{exc}")
            return

        size = self._target_size()
        jobs: list[ConvertJob] = []
        used_names: set[str] = set()
        for src in self._sources:
            name = f"{src.stem}.svg"
            if name in used_names or (out_dir / name).exists():
                # avoid overwrite within batch / existing files
                n = 2
                while True:
                    candidate = f"{src.stem}_{n}.svg"
                    if candidate not in used_names and not (out_dir / candidate).exists():
                        name = candidate
                        break
                    n += 1
            used_names.add(name)
            jobs.append(ConvertJob(source=src, destination=out_dir / name, target_size=size))

        self.results_list.clear()
        self._set_busy(True)

        self._thread = QThread(self)
        self._worker = ConvertWorker(jobs)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self._append_log)
        self._worker.item_done.connect(self._on_item_done)
        self._worker.finished.connect(self._on_conversion_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_worker)
        self._thread.start()

    def _set_busy(self, busy: bool) -> None:
        self.convert_btn.setEnabled(not busy)
        self.convert_btn.setText("…" if busy else "⚡\nCONVERT")

    def _on_item_done(self, result: ConvertResult) -> None:
        if result.ok and result.destination is not None:
            text = (
                f"OK  {result.destination.name}  "
                f"({self._target_size()}x{self._target_size()})"
            )
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, str(result.destination))
            item.setToolTip(str(result.destination))
            item.setSizeHint(QSize(0, 32))
        else:
            item = QListWidgetItem(f"ERR  {result.source.name} — {result.message}")
            item.setForeground(Qt.GlobalColor.red)
            item.setData(Qt.ItemDataRole.UserRole, None)
            item.setToolTip(result.message)
            item.setSizeHint(QSize(0, 32))
        self.results_list.addItem(item)
        self.results_list.scrollToItem(item)

    def _view_result_item(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            _open_path(Path(path))

    def _view_selected_result(self) -> None:
        item = self.results_list.currentItem()
        if item is None:
            QMessageBox.information(self, "Pixicon", "Select a converted file first.")
            return
        self._view_result_item(item)

    def _on_conversion_finished(self, ok_count: int, err_count: int) -> None:
        self._set_busy(False)
        if err_count and not ok_count:
            QMessageBox.warning(
                self,
                "Pixicon",
                f"Conversion finished with errors.\n{ok_count} succeeded, {err_count} failed.",
            )

    def _cleanup_worker(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
        if self._thread is not None:
            self._thread.deleteLater()
            self._thread = None

    def _append_log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log_view.appendPlainText(f"[{stamp}] {message}")

    def closeEvent(self, event) -> None:  # noqa: ANN001
        if self._worker is not None:
            self._worker.request_cancel()
        if self._thread is not None and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(2000)
        super().closeEvent(event)
