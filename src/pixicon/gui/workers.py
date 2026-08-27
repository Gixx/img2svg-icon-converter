"""Background conversion worker."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from PySide6.QtCore import QObject, Signal, Slot

from pixicon.core.convert import convert_file, ico_square_sizes, pick_ico_size
from pixicon.core.validate import ValidationError


@dataclass(frozen=True)
class ConvertJob:
    source: Path
    destination: Path
    target_size: int


@dataclass(frozen=True)
class ConvertResult:
    source: Path
    destination: Path | None
    ok: bool
    message: str


class ConvertWorker(QObject):
    log = Signal(str)
    item_done = Signal(object)  # ConvertResult
    finished = Signal(int, int)  # success_count, error_count

    def __init__(self, jobs: list[ConvertJob], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._jobs = jobs
        self._cancel = False

    def request_cancel(self) -> None:
        self._cancel = True

    @Slot()
    def run(self) -> None:
        ok_count = 0
        err_count = 0
        total = len(self._jobs)
        if total == 0:
            self.log.emit("No files to convert.")
            self.finished.emit(0, 0)
            return

        size = self._jobs[0].target_size
        self.log.emit(
            f"Conversion started ({total} file(s), target {size}x{size})..."
        )

        for job in self._jobs:
            if self._cancel:
                self.log.emit("Conversion cancelled.")
                break
            try:
                frame_note = ""
                with Image.open(job.source) as im:
                    edges = ico_square_sizes(im)
                    if edges:
                        chosen = pick_ico_size(edges, target_size=job.target_size)
                        frame_note = f" [ICO frame {chosen}x{chosen}]"
                convert_file(job.source, job.destination, target_size=job.target_size)
                ok_count += 1
                msg = f"OK  {job.source.name} → {job.destination.name}{frame_note}"
                self.log.emit(msg)
                self.item_done.emit(
                    ConvertResult(
                        source=job.source,
                        destination=job.destination,
                        ok=True,
                        message=msg,
                    )
                )
            except ValidationError as exc:
                err_count += 1
                msg = f"ERROR  {job.source.name}: {exc}"
                self.log.emit(msg)
                self.item_done.emit(
                    ConvertResult(
                        source=job.source,
                        destination=None,
                        ok=False,
                        message=str(exc),
                    )
                )
            except Exception as exc:  # noqa: BLE001 - worker boundary
                err_count += 1
                msg = f"ERROR  {job.source.name}: {exc}"
                self.log.emit(msg)
                self.item_done.emit(
                    ConvertResult(
                        source=job.source,
                        destination=None,
                        ok=False,
                        message=str(exc),
                    )
                )

        self.log.emit(f"Summary: {ok_count} succeeded, {err_count} failed. Done.")
        self.finished.emit(ok_count, err_count)
