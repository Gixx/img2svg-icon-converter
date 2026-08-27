"""Application entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from pixicon.gui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else [sys.argv[0], *argv])
    app = QApplication(args)
    app.setApplicationName("Pixicon")
    app.setOrganizationName("Pixicon")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
