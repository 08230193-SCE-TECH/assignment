"""Logic layer: quiz rules, scoring and input validation.

This file has NO GUI code, so it can be tested without opening a window.
"""

from dataclasses import dataclass

import config
from models import Question


# ---------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------

def grade_for(percent: float) -> str:
    """Turn a percentage into a grade label."""
    if percent >= 80:
        return "A - Excellent"
    if percent >= 65:
        return "B - Good"
    if percent >= 50:
        return "C - Pass"
    return "F - Try again"


def feedback_for(percent: float) -> str:
    """A short encouraging message shown on the result screen."""
    if percent >= 80:
        return "Excellent work! You really know this topic."
    if percent >= 65:
        return "Good job - keep it up!"
    if percent >= 50:
        return "You passed. A little more practice will make you even better."
    return "Don't give up - read the review below and try again."


@dataclass
class AnswerRecord:
    """The player's answer to one question."""

    question: Question
    chosen_index: int | None        # None means skipped / time ran out

    @property
    def is_correct(self) -> bool:
        return self.chosen_index == self.question.correct_index

    @property
    def chosen_text(self) -> str:
        if self.chosen_index is None:
            return "No answer (time ran out)"
        return self.question.options[self.chosen_index]


class QuizSession:
    """Keeps track of one quiz attempt from the first to the last question."""

    def __init__(self, player_name: str, category: str,
                 questions: list[Question], seconds_per_question: int):
        if not questions:
            raise ValueError("A quiz needs at least one question.")
        self.player_name = player_name
        self.category = category
        self.questions = questions
        self.seconds_per_question = seconds_per_question
        self.answers: list[AnswerRecord] = []

    # --- progress -------------------------------------------------
    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def is_finished(self) -> bool:
        return len(self.answers) >= self.total

    @property
    def current_number(self) -> int:
        """1-based number of the question being shown."""
        return len(self.answers) + 1

    @property
    def is_last_question(self) -> bool:
        return len(self.answers) == self.total - 1

    @property
    def current_question(self) -> Question:
        return self.questions[len(self.answers)]

    def submit_answer(self, chosen_index: int | None) -> AnswerRecord:
        """Record the answer for the current question and move on."""
        if self.is_finished:
            raise RuntimeError("The quiz is already finished.")
        if chosen_index is not None and not 0 <= chosen_index <= 3:
            raise ValueError("Answer index must be 0-3 or None.")
        record = AnswerRecord(self.current_question, chosen_index)
        self.answers.append(record)
        return record

    # --- score ----------------------------------------------------
    @property
    def correct_count(self) -> int:
        return sum(1 for record in self.answers if record.is_correct)

    @property
    def percent(self) -> float:
        return round(self.correct_count / self.total * 100, 1)

    @property
    def grade(self) -> str:
        return grade_for(self.percent)

    @property
    def passed(self) -> bool:
        return self.percent >= config.PASS_PERCENT


# ---------------------------------------------------------------
# Input validation (each returns an error message, or None if OK)
# ---------------------------------------------------------------

def validate_player_name(name: str) -> str | None:
    name = name.strip()
    if not name:
        return "Please enter your name before starting the quiz."
    if len(name) < 5:
        return "Your name must have at least 5 characters."
    if len(name) > 30:
        return "Your name must be 30 characters or fewer."
    return None


def validate_question_fields(category: str, text: str,
                             options: list[str], correct_index: int) -> str | None:
    category = category.strip()
    text = text.strip()
    cleaned = [option.strip() for option in options]

    if not category:
        return "Please choose or type a category."
    if len(category) > 30:
        return "The category must be 30 characters or fewer."
    if len(text) < 5:
        return "The question must have at least 5 characters."
    if any(not option for option in cleaned):
        return "All four answer options must be filled in."
    if len({option.lower() for option in cleaned}) < 4:
        return "The four answer options must all be different."
    if not 0 <= correct_index <= 3:
        return "Please select which option is correct."
    return None
