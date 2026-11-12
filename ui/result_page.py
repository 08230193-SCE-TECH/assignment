"""Result screen: shows the score and a review of every answer."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QTableWidget, QVBoxLayout, QWidget,
)

from quiz_logic import QuizSession, feedback_for
from ui.helpers import make_item, use_hand_cursor

GREEN = QColor("#16a34a")
RED = QColor("#dc2626")


class ResultPage(QWidget):
    home_requested = pyqtSignal()
    retry_requested = pyqtSignal()
    report_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 24, 40, 24)
        layout.setSpacing(12)

        # Summary card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 18, 24, 18)
        card_layout.setSpacing(2)

        self.heading_label = QLabel("Quiz Complete!")
        self.heading_label.setObjectName("title")
        self.player_label = QLabel()
        self.player_label.setObjectName("subtitle")
        self.score_label = QLabel()
        self.score_label.setObjectName("bigScore")
        self.percent_label = QLabel()
        self.percent_label.setObjectName("heading")
        self.status_label = QLabel()
        self.feedback_label = QLabel()
        self.feedback_label.setObjectName("subtitle")
        for label in (self.heading_label, self.player_label, self.score_label,
                      self.percent_label, self.status_label, self.feedback_label):
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(label)
        layout.addWidget(card)

        review_title = QLabel("Review your answers")
        review_title.setObjectName("heading")
        layout.addWidget(review_title)

        # Review table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["#", "Question", "Your answer", "Correct answer", "Result"]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Buttons
        buttons = QHBoxLayout()
        self.report_button = QPushButton("View Score Report")
        self.retry_button = QPushButton("Try Again")
        self.retry_button.setToolTip("Take the same quiz again with the same settings")
        self.home_button = QPushButton("Back to Home")
        self.home_button.setObjectName("primary")
        use_hand_cursor(self.report_button, self.retry_button, self.home_button)
        buttons.addStretch()
        buttons.addWidget(self.report_button)
        buttons.addWidget(self.retry_button)
        buttons.addWidget(self.home_button)
        layout.addLayout(buttons)

        self.home_button.clicked.connect(self.home_requested)
        self.report_button.clicked.connect(self.report_requested)
        self.retry_button.clicked.connect(self.retry_requested)

    def show_result(self, session: QuizSession):
        """Fill the screen from a finished quiz session."""
        self.player_label.setText(f"{session.player_name}  -  {session.category}")
        self.score_label.setText(f"{session.correct_count} / {session.total}")
        self.percent_label.setText(f"{session.percent:.1f}%    |    Grade: {session.grade}")

        color = "#16a34a" if session.passed else "#dc2626"
        self.status_label.setText("Result: PASSED" if session.passed else "Result: NOT PASSED")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 15px;")

        self.feedback_label.setText(feedback_for(session.percent))

        self.table.setRowCount(0)
        for row, record in enumerate(session.answers):
            self.table.insertRow(row)
            self.table.setItem(row, 0, make_item(row + 1))
            self.table.setItem(row, 1, make_item(record.question.text, centered=False))
            self.table.setItem(row, 2, make_item(record.chosen_text, centered=False))
            self.table.setItem(row, 3, make_item(record.question.correct_answer, centered=False))
            result = make_item("Correct" if record.is_correct else "Wrong")
            result.setForeground(GREEN if record.is_correct else RED)
            self.table.setItem(row, 4, result)
