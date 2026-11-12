"""Main window: menu bar + a stack of screens (home, quiz, result)."""

import sqlite3

from PyQt6.QtCore import PYQT_VERSION_STR
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

import config
import database
from quiz_logic import QuizSession
from ui.helpers import ask_yes_no, show_db_error, show_warning
from ui.home_page import HomePage
from ui.manage_questions import ManageQuestionsDialog
from ui.quiz_page import QuizPage
from ui.result_page import ResultPage
from ui.score_report import ScoreReportDialog


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Name and roll number in the title so every screenshot shows them
        self.setWindowTitle(f"{config.APP_NAME} - {config.STUDENT_NAME} ({config.ROLL_NO})")
        self.resize(980, 700)
        self.setMinimumSize(820, 600)

        # Only one screen is visible at a time
        self.last_settings = None          # remembered so "Try Again" can repeat the quiz
        self.stack = QStackedWidget()
        self.home_page = HomePage()
        self.quiz_page = QuizPage()
        self.result_page = ResultPage()
        for page in (self.home_page, self.quiz_page, self.result_page):
            self.stack.addWidget(page)
        self.setCentralWidget(self.stack)

        self._create_menu_bar()
        self._connect_signals()
        self.statusBar().showMessage("Ready - enter your name and start a quiz.")

    # ------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------
    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        self._add_action(file_menu, "E&xit", "Ctrl+Q", self.close)

        quiz_menu = menu_bar.addMenu("&Quiz")
        self.quiz_actions = [
            self._add_action(quiz_menu, "&New Quiz", "Ctrl+N", self._go_home),
            self._add_action(quiz_menu, "&Manage Questions", "Ctrl+M", self._open_manage_questions),
            self._add_action(quiz_menu, "&Score Report", "Ctrl+R", self._open_score_report),
        ]

        help_menu = menu_bar.addMenu("&Help")
        self._add_action(help_menu, "&About", "F1", self._show_about)

    def _add_action(self, menu, text, shortcut, slot) -> QAction:
        action = QAction(text, self)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _set_quiz_actions_enabled(self, enabled: bool):
        """Lock the Quiz menu while a quiz is running."""
        for action in self.quiz_actions:
            action.setEnabled(enabled)

    # ------------------------------------------------------------
    # Wiring the screens together
    # ------------------------------------------------------------
    def _connect_signals(self):
        self.home_page.start_requested.connect(self._start_quiz)
        self.quiz_page.finished.connect(self._quiz_finished)
        self.quiz_page.quit_requested.connect(self._go_home)
        self.result_page.home_requested.connect(self._go_home)
        self.result_page.retry_requested.connect(self._retry_quiz)
        self.result_page.report_requested.connect(self._open_score_report)

    # ------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------
    def _retry_quiz(self):
        """Result screen > Try Again: repeat the last quiz with the same settings."""
        if self.last_settings is not None:
            self._start_quiz(*self.last_settings)

    def _start_quiz(self, name, category_text, count, seconds, shuffle):
        self.last_settings = (name, category_text, count, seconds, shuffle)
        category = None if category_text == config.ALL_CATEGORIES else category_text
        try:
            questions = database.get_questions_for_quiz(category, count, shuffle)
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        if not questions:
            show_warning(self, "No Questions", "There are no questions in this category.")
            return

        session = QuizSession(name, category_text, questions, seconds)
        self.quiz_page.start(session)
        self.stack.setCurrentWidget(self.quiz_page)
        self._set_quiz_actions_enabled(False)
        self.statusBar().showMessage(f"Quiz in progress - good luck, {name}!")

    def _quiz_finished(self, session: QuizSession):
        try:
            database.save_result(
                session.player_name, session.category, session.total,
                session.correct_count, session.percent, session.seconds_per_question,
            )
            message = "Quiz finished - your result was saved."
        except sqlite3.Error as error:
            show_db_error(self, error)                   # still show the result screen
            message = "Quiz finished - but the result could not be saved."

        self.result_page.show_result(session)
        self.stack.setCurrentWidget(self.result_page)
        self._set_quiz_actions_enabled(True)
        self.statusBar().showMessage(message)

    def _go_home(self):
        self.quiz_page.stop()
        self.home_page.refresh_categories()
        self.stack.setCurrentWidget(self.home_page)
        self._set_quiz_actions_enabled(True)
        self.statusBar().showMessage("Ready - enter your name and start a quiz.")

    def _open_manage_questions(self):
        ManageQuestionsDialog(self).exec()
        self.home_page.refresh_categories()              # the bank may have changed

    def _open_score_report(self):
        ScoreReportDialog(self).exec()

    def _show_about(self):
        QMessageBox.about(
            self, f"About {config.APP_NAME}",
            f"<b>{config.APP_NAME}</b> - quiz with timer and score report<br><br>"
            f"Name: {config.STUDENT_NAME}<br>"
            f"Roll No: {config.ROLL_NO}<br>"
            f"Course: {config.COURSE}<br><br>"
            f"Built with Python and PyQt6 {PYQT_VERSION_STR}, data stored in SQLite.",
        )

    def closeEvent(self, event):
        """Ask before closing if a quiz is running."""
        if self.stack.currentWidget() is self.quiz_page:
            if not ask_yes_no(self, "Exit", "A quiz is in progress. Exit anyway?"):
                event.ignore()
                return
            self.quiz_page.stop()
        event.accept()
