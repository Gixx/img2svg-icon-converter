"""Dark theme stylesheet matching the Pixicon mockup."""

APP_STYLESHEET = """
QWidget {
    background-color: #1e2430;
    color: #e8ecf1;
    font-family: "Segoe UI", "Ubuntu", "Helvetica Neue", sans-serif;
    font-size: 13px;
}
QMainWindow {
    background-color: #1e2430;
}
QGroupBox {
    border: 1px solid #3a4558;
    border-radius: 6px;
    margin-top: 12px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #c5d0e0;
}
QLineEdit, QComboBox, QListWidget, QPlainTextEdit {
    background-color: #151a24;
    border: 1px solid #3a4558;
    border-radius: 4px;
    padding: 6px 8px;
    selection-background-color: #3b82f6;
}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {
    border-color: #3b82f6;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #151a24;
    border: 1px solid #3a4558;
    selection-background-color: #3b82f6;
}
QPushButton {
    background-color: #2a3444;
    border: 1px solid #3a4558;
    border-radius: 4px;
    padding: 6px 12px;
    color: #e8ecf1;
}
QPushButton:hover {
    background-color: #354054;
}
QPushButton:pressed {
    background-color: #1f2836;
}
QPushButton:disabled {
    color: #6b7585;
    background-color: #252b38;
}
QPushButton#convertButton {
    background-color: #2563eb;
    border: none;
    border-radius: 10px;
    color: white;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 1px;
    min-width: 88px;
    min-height: 88px;
    max-width: 100px;
    max-height: 100px;
}
QPushButton#convertButton:hover {
    background-color: #3b82f6;
}
QPushButton#convertButton:pressed {
    background-color: #1d4ed8;
}
QPushButton#convertButton:disabled {
    background-color: #1e3a5f;
    color: #8aa0c0;
}
QListWidget::item {
    min-height: 28px;
    padding: 8px;
    border-bottom: 1px solid #2a3344;
}
QListWidget#resultsList::item {
    min-height: 30px;
    padding: 10px 8px;
}
QListWidget#sourceList::item {
    min-height: 40px;
    padding: 8px;
}
QListWidget::item:selected {
    background-color: #243047;
}
QPlainTextEdit#processLog {
    font-family: "Cascadia Code", "Consolas", "Ubuntu Mono", monospace;
    font-size: 12px;
    background-color: #0d1118;
    color: #b8c4d4;
}
QLabel#hintLabel {
    color: #8b97a8;
    font-weight: 400;
}
"""
