"""
main.py — Entry point for Todo Widget
Usage: python3 main.py
"""
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont

from app.ui.main_window import MainWindow


def load_stylesheet(app: QApplication) -> None:
    """Load QSS stylesheet from assets/style.qss"""
    qss_path = Path(__file__).parent / "assets" / "style.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Todo")

    # Use system font as base
    font = QFont()
    font.setPointSize(13)
    app.setFont(font)

    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()