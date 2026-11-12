"""Entry point:  python main.py"""

import sqlite3
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

import database
from ui.main_window import MainWindow
from ui.styles import APP_STYLE


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")                 # same base look on every operating system
    app.setStyleSheet(APP_STYLE)

    try:
        database.init_db()                 # creates tables + sample questions on first run
    except (sqlite3.Error, OSError) as error:
        QMessageBox.critical(None, "Startup Error", f"Could not open the database:\n\n{error}")
        return 1

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
