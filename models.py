"""Plain data classes shared by the data layer, the logic layer and the UI."""

from dataclasses import dataclass

OPTION_LETTERS = ("A", "B", "C", "D")


@dataclass
class Question:
    """One multiple-choice question with exactly four options."""

    question_id: int | None
    category: str
    text: str
    options: list[str]
    correct_index: int          # 0 = A, 1 = B, 2 = C, 3 = D

    @property
    def correct_answer(self) -> str:
        return self.options[self.correct_index]
