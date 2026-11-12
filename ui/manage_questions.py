"""Dialog for adding, editing and deleting questions in the question bank."""

import sqlite3

from PyQt6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QFormLayout, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTextEdit, QVBoxLayout,
)

import database
import quiz_logic
from models import OPTION_LETTERS, Question
from ui.helpers import ask_yes_no, make_item, show_db_error, show_warning, use_hand_cursor


class ManageQuestionsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Questions")
        self.resize(1120, 660)

        self.selected_id: int | None = None        # id of the row being edited
        self.questions: list[Question] = []        # same order as the table rows

        self._build_ui()
        self._load_categories()
        self._load_table()

    # ------------------------------------------------------------
    # Building the dialog
    # ------------------------------------------------------------
    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(16)

        # ----- left: form card -----
        form_card = QFrame()
        form_card.setObjectName("card")
        form_card.setFixedWidth(400)
        card_layout = QVBoxLayout(form_card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(10)

        heading = QLabel("Question Details")
        heading.setObjectName("heading")
        card_layout.addWidget(heading)

        top_form = QFormLayout()
        self.category_input = QComboBox()
        self.category_input.setEditable(True)           # pick one or type a new category
        top_form.addRow("Category:", self.category_input)
        self.question_input = QTextEdit()
        self.question_input.setFixedHeight(80)
        self.question_input.setPlaceholderText("Type the question here")
        top_form.addRow("Question:", self.question_input)
        card_layout.addLayout(top_form)

        # Options A-D in a grid: letter on the left, text box on the right
        options_grid = QGridLayout()
        self.option_inputs: list[QLineEdit] = []
        for row, letter in enumerate(OPTION_LETTERS):
            options_grid.addWidget(QLabel(f"Option {letter}:"), row, 0)
            line_edit = QLineEdit()
            options_grid.addWidget(line_edit, row, 1)
            self.option_inputs.append(line_edit)
        card_layout.addLayout(options_grid)

        correct_form = QFormLayout()
        self.correct_combo = QComboBox()
        self.correct_combo.addItems([f"Option {letter}" for letter in OPTION_LETTERS])
        correct_form.addRow("Correct answer:", self.correct_combo)
        card_layout.addLayout(correct_form)

        # Buttons in a 2 x 2 grid
        buttons = QGridLayout()
        self.add_button = QPushButton("Add Question")
        self.add_button.setObjectName("primary")
        self.update_button = QPushButton("Update Selected")
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setObjectName("danger")
        self.clear_button = QPushButton("Clear Form")
        buttons.addWidget(self.add_button, 0, 0)
        buttons.addWidget(self.update_button, 0, 1)
        buttons.addWidget(self.delete_button, 1, 0)
        buttons.addWidget(self.clear_button, 1, 1)
        card_layout.addLayout(buttons)
        use_hand_cursor(self.add_button, self.update_button, self.delete_button,
                        self.clear_button, self.category_input, self.correct_combo)
        self.add_button.setToolTip("Save the form as a new question")
        self.update_button.setToolTip("Save changes to the question selected in the table")
        self.delete_button.setToolTip("Delete the question selected in the table")

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        card_layout.addWidget(self.message_label)
        card_layout.addStretch()

        main_layout.addWidget(form_card)

        # ----- right: question table -----
        right = QVBoxLayout()
        self.count_label = QLabel()
        self.count_label.setObjectName("heading")
        right.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Category", "Question", "Correct Answer"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        right.addWidget(self.table)
        main_layout.addLayout(right)

        # Events
        self.add_button.clicked.connect(self._on_add)
        self.update_button.clicked.connect(self._on_update)
        self.delete_button.clicked.connect(self._on_delete)
        self.clear_button.clicked.connect(self._clear_form)
        self.table.itemSelectionChanged.connect(self._on_row_selected)

    # ------------------------------------------------------------
    # Loading data
    # ------------------------------------------------------------
    def _load_categories(self):
        """Fill the category drop-down, keeping whatever is currently typed."""
        typed = self.category_input.currentText()
        try:
            categories = database.get_categories()
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        self.category_input.clear()
        self.category_input.addItems(categories)
        self.category_input.setCurrentText(typed)

    def _load_table(self):
        try:
            self.questions = database.get_all_questions()
        except sqlite3.Error as error:
            show_db_error(self, error)
            return

        self.table.setRowCount(0)
        for row, question in enumerate(self.questions):
            self.table.insertRow(row)
            self.table.setItem(row, 0, make_item(question.question_id))
            self.table.setItem(row, 1, make_item(question.category, centered=False))
            self.table.setItem(row, 2, make_item(question.text, centered=False))
            self.table.setItem(row, 3, make_item(question.correct_answer, centered=False))
        self.count_label.setText(f"Question Bank ({len(self.questions)})")
        self.selected_id = None

    # ------------------------------------------------------------
    # Form helpers
    # ------------------------------------------------------------
    def _set_message(self, text: str, ok: bool = True):
        color = "#16a34a" if ok else "#dc2626"
        self.message_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.message_label.setText(text)

    def _read_form(self):
        """Return (category, text, options, correct_index) from the form."""
        return (
            self.category_input.currentText().strip(),
            self.question_input.toPlainText().strip(),
            [box.text().strip() for box in self.option_inputs],
            self.correct_combo.currentIndex(),
        )

    def _clear_form(self):
        self.selected_id = None
        self.category_input.setCurrentText("")
        self.question_input.clear()
        for box in self.option_inputs:
            box.clear()
        self.correct_combo.setCurrentIndex(0)
        self.table.clearSelection()
        self.message_label.setText("")

    # ------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------
    def _on_row_selected(self):
        """A table row was clicked: copy that question into the form."""
        items = self.table.selectedItems()
        if not items:
            return
        question = self.questions[items[0].row()]
        self.selected_id = question.question_id
        self.category_input.setCurrentText(question.category)
        self.question_input.setPlainText(question.text)
        for box, option in zip(self.option_inputs, question.options):
            box.setText(option)
        self.correct_combo.setCurrentIndex(question.correct_index)
        self.message_label.setText("")

    def _on_add(self):
        category, text, options, correct = self._read_form()
        error = quiz_logic.validate_question_fields(category, text, options, correct)
        if error:
            show_warning(self, "Invalid Question", error)
            return
        try:
            database.add_question(category, text, options, correct)
        except ValueError as error:
            show_warning(self, "Cannot Add Question", str(error))
            return
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        self._clear_form()
        self._load_categories()
        self._load_table()
        self._set_message("Question added successfully.")

    def _on_update(self):
        if self.selected_id is None:
            show_warning(self, "Nothing Selected", "Click a question in the table first.")
            return
        category, text, options, correct = self._read_form()
        error = quiz_logic.validate_question_fields(category, text, options, correct)
        if error:
            show_warning(self, "Invalid Question", error)
            return
        try:
            database.update_question(self.selected_id, category, text, options, correct)
        except ValueError as error:
            show_warning(self, "Cannot Update Question", str(error))
            return
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        self._load_categories()
        self._load_table()
        self._set_message("Question updated.")

    def _on_delete(self):
        if self.selected_id is None:
            show_warning(self, "Nothing Selected", "Click a question in the table first.")
            return
        if not ask_yes_no(self, "Delete Question", "Delete the selected question permanently?"):
            return
        try:
            database.delete_question(self.selected_id)
        except ValueError as error:
            show_warning(self, "Cannot Delete Question", str(error))
            return
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        self._clear_form()
        self._load_categories()
        self._load_table()
        self._set_message("Question deleted.")
