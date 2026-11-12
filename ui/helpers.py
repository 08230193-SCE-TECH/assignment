"""Small shared UI helpers (message boxes and table cells)."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem


def show_warning(parent, title: str, text: str) -> None:
    QMessageBox.warning(parent, title, text)


def show_db_error(parent, error: Exception) -> None:
    QMessageBox.critical(
        parent, "Database Error",
        f"Something went wrong while reading or saving data:\n\n{error}",
    )


def ask_yes_no(parent, title: str, text: str) -> bool:
    """Show a Yes/No question (default answer is No) and return True for Yes."""
    answer = QMessageBox.question(
        parent, title, text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return answer == QMessageBox.StandardButton.Yes


def use_hand_cursor(*widgets) -> None:
    """Show the pointing-hand cursor over clickable widgets (friendlier to use)."""
    for widget in widgets:
        widget.setCursor(Qt.CursorShape.PointingHandCursor)


def make_item(text: str, centered: bool = True) -> QTableWidgetItem:
    """Create a read-only-looking table cell."""
    item = QTableWidgetItem(str(text))
    if centered:
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item
