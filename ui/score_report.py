"""Score report: summary numbers, a chart of recent scores and the full history."""

import csv
import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QDialog, QFileDialog, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QTableWidget, QVBoxLayout,
)

import config
import database
from ui.helpers import ask_yes_no, make_item, show_db_error, show_warning, use_hand_cursor
from ui.score_chart import ScoreChart

TABLE_HEADERS = ["Date", "Player", "Category", "Correct", "Percent", "Time per Q"]


def _make_stat_card(caption: str):
    """A small white card with a big number and a caption under it."""
    card = QFrame()
    card.setObjectName("card")
    layout = QVBoxLayout(card)
    value = QLabel("0")
    value.setObjectName("statValue")
    value.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title = QLabel(caption)
    title.setObjectName("statTitle")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(value)
    layout.addWidget(title)
    return card, value


class ScoreReportDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Score Report")
        self.resize(900, 700)
        self.display_rows: list[list[str]] = []     # what the table currently shows
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        heading = QLabel("Score Report")
        heading.setObjectName("title")
        layout.addWidget(heading)

        # Three summary cards side by side
        cards = QHBoxLayout()
        card1, self.attempts_value = _make_stat_card("Total attempts")
        card2, self.best_value = _make_stat_card("Best score")
        card3, self.average_value = _make_stat_card("Average score")
        for card in (card1, card2, card3):
            cards.addWidget(card)
        layout.addLayout(cards)

        chart_title = QLabel("Latest 10 attempts (green = pass, red = below pass mark)")
        chart_title.setObjectName("hint")
        layout.addWidget(chart_title)
        self.chart = ScoreChart()
        layout.addWidget(self.chart)

        # Filter row
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter by player:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Type part of a name")
        filter_row.addWidget(self.filter_input)
        layout.addLayout(filter_row)

        # History table
        self.table = QTableWidget()
        self.table.setColumnCount(len(TABLE_HEADERS))
        self.table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Buttons
        buttons = QHBoxLayout()
        self.export_button = QPushButton("Export to CSV")
        self.clear_button = QPushButton("Clear History")
        self.clear_button.setObjectName("danger")
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("primary")
        buttons.addWidget(self.export_button)
        buttons.addWidget(self.clear_button)
        buttons.addStretch()
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)
        use_hand_cursor(self.export_button, self.clear_button, self.close_button)
        self.export_button.setToolTip("Save the table below as a CSV file (opens in Excel)")

        # Events
        self.filter_input.textChanged.connect(self._load)
        self.export_button.clicked.connect(self._on_export)
        self.clear_button.clicked.connect(self._on_clear)
        self.close_button.clicked.connect(self.accept)

    # ------------------------------------------------------------
    def _load(self, _text: str = ""):
        """Reload the summary, chart and table (table respects the filter)."""
        try:
            rows = database.get_results(self.filter_input.text().strip())
            attempts, best, average = database.get_summary()
            recent = database.get_recent_scores(10)
        except sqlite3.Error as error:
            show_db_error(self, error)
            return

        self.attempts_value.setText(str(attempts))
        self.best_value.setText(f"{best:.1f}%")
        self.average_value.setText(f"{average:.1f}%")
        self.chart.set_scores(recent)

        self.display_rows = []
        self.table.setRowCount(0)
        for row_number, row in enumerate(rows):
            values = [
                row["taken_on"],
                row["player_name"],
                row["category"],
                f"{row['correct_answers']} / {row['total_questions']}",
                f"{row['score_percent']:.1f}%",
                f"{row['seconds_per_question']} s",
            ]
            self.display_rows.append(values)
            self.table.insertRow(row_number)
            for column, value in enumerate(values):
                item = make_item(value)
                if column == 4:                       # colour the percent column
                    passed = row["score_percent"] >= config.PASS_PERCENT
                    item.setForeground(QColor("#16a34a" if passed else "#dc2626"))
                self.table.setItem(row_number, column, item)

    def _on_export(self):
        if not self.display_rows:
            show_warning(self, "Nothing to Export", "There are no results to export yet.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Score Report", "quiz_results.csv", "CSV files (*.csv)"
        )
        if not path:                                   # user pressed Cancel
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(TABLE_HEADERS)
                writer.writerows(self.display_rows)
        except OSError as error:
            show_warning(self, "Export Failed", f"Could not save the file:\n{error}")

    def _on_clear(self):
        if not ask_yes_no(self, "Clear History",
                          "Delete ALL saved quiz results? This cannot be undone."):
            return
        try:
            database.clear_results()
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        self._load()
