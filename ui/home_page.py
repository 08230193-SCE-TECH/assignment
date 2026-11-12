"""Home screen: the player chooses name, category, number of questions and time."""

import sqlite3

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSlider, QSpinBox, QVBoxLayout, QWidget,
)

import config
import database
import quiz_logic
from ui.helpers import show_db_error, show_warning, use_hand_cursor


class HomePage(QWidget):
    # name, category, number of questions, seconds per question, shuffle?
    start_requested = pyqtSignal(str, str, int, int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._available_text = ""
        self._build_ui()
        self.refresh_categories()

    # ------------------------------------------------------------
    # Building the screen
    # ------------------------------------------------------------
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 30, 40, 30)

        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(580)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(14)

        title = QLabel("Welcome to Quiz Master")
        title.setObjectName("title")
        subtitle = QLabel("Answer every question before the timer runs out.")
        subtitle.setObjectName("subtitle")
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)

        # Form: label on the left, input on the right
        form = QFormLayout()
        form.setVerticalSpacing(14)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setMaxLength(30)
        self.name_input.setToolTip("Your name is saved with your score")
        form.addRow("Your name:", self.name_input)

        self.category_combo = QComboBox()
        form.addRow("Category:", self.category_combo)

        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, config.MAX_QUESTIONS_PER_QUIZ)
        self.count_spin.setValue(10)
        form.addRow("Questions:", self.count_spin)

        self.seconds_slider = QSlider(Qt.Orientation.Horizontal)
        self.seconds_slider.setRange(config.MIN_SECONDS, config.MAX_SECONDS)
        self.seconds_slider.setValue(config.DEFAULT_SECONDS)
        self.seconds_slider.setToolTip("Drag to change how long you get for each question")
        self.seconds_label = QLabel(f"{config.DEFAULT_SECONDS} s")
        self.seconds_label.setMinimumWidth(50)
        seconds_row = QHBoxLayout()
        seconds_row.addWidget(self.seconds_slider)
        seconds_row.addWidget(self.seconds_label)
        form.addRow("Time per question:", seconds_row)

        self.shuffle_check = QCheckBox("Shuffle the questions")
        self.shuffle_check.setChecked(True)
        form.addRow("", self.shuffle_check)

        card_layout.addLayout(form)

        self.available_label = QLabel()
        self.available_label.setObjectName("hint")
        card_layout.addWidget(self.available_label)

        self.start_button = QPushButton("Start Quiz")
        self.start_button.setObjectName("primary")
        self.start_button.setToolTip("Begin the quiz (or press Enter in the name box)")
        use_hand_cursor(self.start_button, self.category_combo, self.count_spin,
                        self.seconds_slider, self.shuffle_check)
        card_layout.addWidget(self.start_button)

        outer.addStretch()
        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch()

        # Events (signals -> slots)
        self.category_combo.currentTextChanged.connect(self._update_available)
        self.seconds_slider.valueChanged.connect(self._update_seconds_label)
        self.start_button.clicked.connect(self._on_start_clicked)
        self.name_input.returnPressed.connect(self._on_start_clicked)
        self.name_input.textChanged.connect(self._on_name_changed)

    # ------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------
    def _update_seconds_label(self, value: int):
        """Slider moved: show the new number of seconds."""
        self.seconds_label.setText(f"{value} s")

    def _show_hint(self, text: str, is_error: bool = False):
        """Show a small message under the form (red when it is an error)."""
        self.available_label.setText(text)
        self.available_label.setObjectName("errorHint" if is_error else "hint")
        self.available_label.style().unpolish(self.available_label)   # re-apply the stylesheet
        self.available_label.style().polish(self.available_label)

    def _on_name_changed(self, text: str):
        """Live feedback while typing the name."""
        if len(text.strip()) < 5:
            self._show_hint("Your name needs at least 5 characters.", is_error=True)
        else:
            self._show_hint(self._available_text)

    def _selected_category(self) -> str | None:
        """Category name, or None when 'All Categories' is selected."""
        text = self.category_combo.currentText()
        return None if text in ("", config.ALL_CATEGORIES) else text

    def _update_available(self, _text: str = ""):
        """Category changed: refresh how many questions can be asked."""
        try:
            available = database.count_questions(self._selected_category())
        except sqlite3.Error as error:
            show_db_error(self, error)
            available = 0

        if available == 0:
            self._available_text = "No questions here yet. Add some in Quiz > Manage Questions."
            self._show_hint(self._available_text)
            self.count_spin.setEnabled(False)
            self.start_button.setEnabled(False)
            return

        maximum = min(available, config.MAX_QUESTIONS_PER_QUIZ)
        self.count_spin.setRange(1, maximum)          # also clamps the current value
        self.count_spin.setEnabled(True)
        self.start_button.setEnabled(True)
        self._available_text = f"{available} questions available in this category."
        self._show_hint(self._available_text)

    def _on_start_clicked(self):
        """Validate the name, then tell the main window to start the quiz."""
        name = self.name_input.text().strip()
        error = quiz_logic.validate_player_name(name)
        if error:
            show_warning(self, "Name Needed", error)
            self.name_input.setFocus()
            return
        if not self.start_button.isEnabled():
            return
        self.start_requested.emit(
            name,
            self.category_combo.currentText(),
            self.count_spin.value(),
            self.seconds_slider.value(),
            self.shuffle_check.isChecked(),
        )

    # ------------------------------------------------------------
    # Called by the main window
    # ------------------------------------------------------------
    def refresh_categories(self):
        """Reload the category list (e.g. after questions were added/deleted)."""
        previous = self.category_combo.currentText()
        try:
            categories = database.get_categories()
        except sqlite3.Error as error:
            show_db_error(self, error)
            return

        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem(config.ALL_CATEGORIES)
        self.category_combo.addItems(categories)
        index = self.category_combo.findText(previous)
        self.category_combo.setCurrentIndex(index if index >= 0 else 0)
        self.category_combo.blockSignals(False)
        self._update_available()
