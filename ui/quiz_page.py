"""Quiz screen: shows one question at a time with a countdown timer."""

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QButtonGroup, QFrame, QGroupBox, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QRadioButton, QVBoxLayout, QWidget,
)

from models import OPTION_LETTERS
from quiz_logic import QuizSession
from ui.helpers import ask_yes_no, show_warning, use_hand_cursor


class QuizPage(QWidget):
    finished = pyqtSignal(object)      # sends the finished QuizSession
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.session: QuizSession | None = None
        self.remaining = 0                       # seconds left for this question

        # The timer fires once per second and calls _on_tick
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)

        self._build_ui()

    # ------------------------------------------------------------
    # Building the screen
    # ------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 24, 48, 24)
        layout.setSpacing(12)

        # Top row: question counter on the left, time left on the right
        top_row = QHBoxLayout()
        self.counter_label = QLabel()
        self.counter_label.setObjectName("heading")
        self.time_label = QLabel()
        top_row.addWidget(self.counter_label)
        top_row.addStretch()
        top_row.addWidget(self.time_label)
        layout.addLayout(top_row)

        # Two progress bars: quiz progress and time remaining
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.time_bar = QProgressBar()
        self.time_bar.setTextVisible(False)
        self.time_bar.setFixedHeight(10)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.time_bar)

        # Question text inside a white card
        question_card = QFrame()
        question_card.setObjectName("card")
        question_layout = QVBoxLayout(question_card)
        question_layout.setContentsMargins(24, 20, 24, 20)
        self.question_label = QLabel()
        self.question_label.setObjectName("question")
        self.question_label.setWordWrap(True)
        question_layout.addWidget(self.question_label)
        layout.addWidget(question_card)

        # Four radio buttons in one group: only one can be selected
        options_box = QGroupBox("Choose one answer")
        options_layout = QVBoxLayout(options_box)
        self.option_group = QButtonGroup(self)
        self.option_buttons: list[QRadioButton] = []
        for index in range(4):
            radio = QRadioButton()
            options_layout.addWidget(radio)
            self.option_group.addButton(radio, index)      # id = option index
            self.option_buttons.append(radio)
        layout.addWidget(options_box)

        tip_label = QLabel("Tip: press 1-4 (or A-D) to choose an answer, and Enter to continue.")
        tip_label.setObjectName("hint")
        layout.addWidget(tip_label)

        self.status_label = QLabel()
        self.status_label.setObjectName("errorHint")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Bottom row: quit on the left, next on the right
        bottom_row = QHBoxLayout()
        self.quit_button = QPushButton("Quit Quiz")
        self.quit_button.setObjectName("danger")
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("primary")
        bottom_row.addWidget(self.quit_button)
        bottom_row.addStretch()
        bottom_row.addWidget(self.next_button)
        layout.addLayout(bottom_row)

        self.next_button.clicked.connect(self._on_next_clicked)
        self.quit_button.clicked.connect(self._on_quit_clicked)

        self.quit_button.setToolTip("Leave the quiz without saving")
        self.next_button.setToolTip("Confirm your answer (Enter)")
        use_hand_cursor(self.quit_button, self.next_button, *self.option_buttons)

        # Keyboard shortcuts: 1-4 or A-D pick an option, Enter goes to the next question
        for index in range(4):
            for key in (str(index + 1), OPTION_LETTERS[index]):
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(lambda i=index: self._select_option(i))
        for key in ("Return", "Enter"):
            QShortcut(QKeySequence(key), self).activated.connect(self._on_next_clicked)

    # ------------------------------------------------------------
    # Public methods used by the main window
    # ------------------------------------------------------------
    def start(self, session: QuizSession):
        """Begin a new quiz."""
        self.session = session
        self.status_label.setText("")
        self._show_question()

    def stop(self):
        """Stop the countdown (used when leaving the page or closing the app)."""
        self.timer.stop()

    # ------------------------------------------------------------
    # Showing a question
    # ------------------------------------------------------------
    def _show_question(self):
        session = self.session
        question = session.current_question

        self.counter_label.setText(
            f"Question {session.current_number} of {session.total}  -  {question.category}"
        )
        self.question_label.setText(question.text)
        for index, radio in enumerate(self.option_buttons):
            radio.setText(f"{OPTION_LETTERS[index]}.   {question.options[index]}")

        # Un-tick the previously chosen radio button
        self.option_group.setExclusive(False)
        for radio in self.option_buttons:
            radio.setChecked(False)
        self.option_group.setExclusive(True)

        self.progress_bar.setMaximum(session.total)
        self.progress_bar.setValue(len(session.answers))
        self.next_button.setText("Finish" if session.is_last_question else "Next")

        self.remaining = session.seconds_per_question
        self._update_time_display()
        self.timer.start()

    def _update_time_display(self):
        total = self.session.seconds_per_question
        ratio = self.remaining / total
        if ratio > 0.5:
            color = "#16a34a"        # green
        elif ratio > 0.25:
            color = "#f59e0b"        # amber
        else:
            color = "#dc2626"        # red

        self.time_label.setText(f"Time left: {self.remaining} s")
        self.time_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
        self.time_bar.setMaximum(total)
        self.time_bar.setValue(self.remaining)
        self.time_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}"
        )

    # ------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------
    def _on_tick(self):
        """Called every second by the QTimer."""
        self.remaining -= 1
        self._update_time_display()
        if self.remaining <= 0:
            self._submit(None, timed_out=True)

    def _select_option(self, index: int):
        """Keyboard shortcut handler: tick option 0-3."""
        if self.session is None or self.session.is_finished:
            return
        self.option_buttons[index].setChecked(True)

    def _on_next_clicked(self):
        if self.session is None or self.session.is_finished:
            return
        chosen = self.option_group.checkedId()          # -1 when nothing is selected
        if chosen == -1:
            show_warning(
                self, "No Answer Selected",
                "Please choose an answer before continuing.\n"
                "(If you are not sure, wait for the timer to skip the question.)",
            )
            return
        self._submit(chosen)

    def _on_quit_clicked(self):
        self.timer.stop()                               # pause while the dialog is open
        if ask_yes_no(self, "Quit Quiz", "Quit now? Your progress will not be saved."):
            self.quit_requested.emit()
        else:
            self.timer.start()

    def _submit(self, chosen: int | None, timed_out: bool = False):
        """Record the answer and show the next question (or finish)."""
        self.timer.stop()
        self.session.submit_answer(chosen)
        if self.session.is_finished:
            self.finished.emit(self.session)
            return
        self._show_question()
        self.status_label.setText(
            "Time ran out - the previous question was skipped." if timed_out else ""
        )
