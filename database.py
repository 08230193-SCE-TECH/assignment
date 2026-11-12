

import sqlite3
from contextlib import contextmanager
from datetime import datetime

import config
from models import Question

# ---------------------------------------------------------------
# Sample questions inserted the first time the app runs
# (category, question, [A, B, C, D], index of correct option)
# ---------------------------------------------------------------
SAMPLE_QUESTIONS = [
    ("Python", "Which function displays output on the screen in Python?",
     ["input()", "print()", "show()", "echo()"], 1),
    ("Python", "Which symbol starts a single-line comment in Python?",
     ["//", "--", "#", "/*"], 2),
    ("Python", "What does len([1, 2, 3]) return?",
     ["2", "3", "4", "1"], 1),
    ("Python", "Which of these data types is mutable?",
     ["tuple", "str", "int", "list"], 3),
    ("Python", "Which keyword is used to define a function in Python?",
     ["func", "define", "def", "function"], 2),
    ("Python", "What is the usual file extension of a Python script?",
     [".pt", ".py", ".python", ".pyt"], 1),
    ("Computer Basics", "What does CPU stand for?",
     ["Central Processing Unit", "Computer Personal Unit",
      "Central Program Utility", "Core Processing Update"], 0),
    ("Computer Basics", "How many bits are there in one byte?",
     ["4", "16", "8", "10"], 2),
    ("Computer Basics", "RAM is best described as which kind of memory?",
     ["Permanent storage", "Volatile memory", "Optical memory", "Read-only memory"], 1),
    ("Computer Basics", "Which of these is an output device?",
     ["Keyboard", "Mouse", "Scanner", "Monitor"], 3),
    ("Computer Basics", "Which of these is an operating system?",
     ["Python", "Linux", "Excel", "Google"], 1),
    ("Bhutan", "What is the capital of Bhutan?",
     ["Paro", "Punakha", "Thimphu", "Phuntsholing"], 2),
    ("Bhutan", "What is the national animal of Bhutan?",
     ["Takin", "Snow leopard", "Red panda", "Yak"], 0),
    ("Bhutan", "What is the currency of Bhutan called?",
     ["Rupee", "Ngultrum", "Taka", "Baht"], 1),
    ("Bhutan", "Which famous cliffside monastery is located near Paro?",
     ["Punakha Dzong", "Tashichho Dzong", "Taktsang (Tiger's Nest)", "Rinpung Dzong"], 2),
]

INSERT_QUESTION_SQL = """
    INSERT INTO questions
        (category, question_text, option_a, option_b, option_c, option_d, correct_option)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""


# ---------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------

@contextmanager
def get_connection():
    """Open the database, commit on success, roll back on error, always close."""
    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    """Create the tables if needed and add the sample questions once."""
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                category       TEXT NOT NULL,
                question_text  TEXT NOT NULL UNIQUE,
                option_a       TEXT NOT NULL,
                option_b       TEXT NOT NULL,
                option_c       TEXT NOT NULL,
                option_d       TEXT NOT NULL,
                correct_option INTEGER NOT NULL CHECK (correct_option BETWEEN 0 AND 3)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                result_id            INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name          TEXT NOT NULL,
                category             TEXT NOT NULL,
                total_questions      INTEGER NOT NULL,
                correct_answers      INTEGER NOT NULL,
                score_percent        REAL NOT NULL,
                seconds_per_question INTEGER NOT NULL,
                taken_on             TEXT NOT NULL
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        if count == 0:
            conn.executemany(
                INSERT_QUESTION_SQL,
                [(category, text, *options, correct)
                 for category, text, options, correct in SAMPLE_QUESTIONS],
            )


# ---------------------------------------------------------------
# Questions
# ---------------------------------------------------------------

def _row_to_question(row: sqlite3.Row) -> Question:
    return Question(
        question_id=row["question_id"],
        category=row["category"],
        text=row["question_text"],
        options=[row["option_a"], row["option_b"], row["option_c"], row["option_d"]],
        correct_index=row["correct_option"],
    )


def get_categories() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT category FROM questions ORDER BY category"
        ).fetchall()
    return [row["category"] for row in rows]


def count_questions(category: str | None = None) -> int:
    """Number of questions in one category (or in total if category is None)."""
    sql = "SELECT COUNT(*) FROM questions"
    params: list = []
    if category:
        sql += " WHERE category = ?"
        params.append(category)
    with get_connection() as conn:
        return conn.execute(sql, params).fetchone()[0]


def get_questions_for_quiz(category: str | None, limit: int,
                           shuffle: bool) -> list[Question]:
    """Pick the questions for a quiz (random order if shuffle is True)."""
    sql = "SELECT * FROM questions"
    params: list = []
    if category:
        sql += " WHERE category = ?"
        params.append(category)
    sql += " ORDER BY RANDOM()" if shuffle else " ORDER BY question_id"
    sql += " LIMIT ?"
    params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_row_to_question(row) for row in rows]


def get_all_questions() -> list[Question]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM questions ORDER BY category, question_id"
        ).fetchall()
    return [_row_to_question(row) for row in rows]


def add_question(category: str, text: str, options: list[str],
                 correct_index: int) -> int:
    """Insert a question and return its new id."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                INSERT_QUESTION_SQL,
                (category.strip(), text.strip(),
                 *[option.strip() for option in options], correct_index),
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as error:
        if "UNIQUE" in str(error):
            raise ValueError("A question with this exact text already exists.") from error
        raise


def update_question(question_id: int, category: str, text: str,
                    options: list[str], correct_index: int) -> None:
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """UPDATE questions
                   SET category = ?, question_text = ?, option_a = ?, option_b = ?,
                       option_c = ?, option_d = ?, correct_option = ?
                   WHERE question_id = ?""",
                (category.strip(), text.strip(),
                 *[option.strip() for option in options], correct_index, question_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("That question no longer exists.")
    except sqlite3.IntegrityError as error:
        if "UNIQUE" in str(error):
            raise ValueError("Another question already has this exact text.") from error
        raise


def delete_question(question_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM questions WHERE question_id = ?", (question_id,)
        )
        if cursor.rowcount == 0:
            raise ValueError("That question no longer exists.")


# ---------------------------------------------------------------
# Results
# ---------------------------------------------------------------

def save_result(player_name: str, category: str, total_questions: int,
                correct_answers: int, score_percent: float,
                seconds_per_question: int) -> int:
    taken_on = datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO results
               (player_name, category, total_questions, correct_answers,
                score_percent, seconds_per_question, taken_on)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (player_name, category, total_questions, correct_answers,
             score_percent, seconds_per_question, taken_on),
        )
        return cursor.lastrowid


def get_results(name_filter: str = "") -> list[sqlite3.Row]:
    """All attempts, newest first. name_filter matches part of the player name."""
    with get_connection() as conn:
        return conn.execute(
            """SELECT * FROM results
               WHERE player_name LIKE ?
               ORDER BY result_id DESC""",
            (f"%{name_filter}%",),
        ).fetchall()


def get_summary() -> tuple[int, float, float]:
    """Return (number of attempts, best percent, average percent)."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*), MAX(score_percent), AVG(score_percent) FROM results"
        ).fetchone()
    return row[0], row[1] or 0.0, row[2] or 0.0


def get_recent_scores(limit: int = 10) -> list[float]:
    """Percent scores of the latest attempts, oldest first (for the chart)."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT score_percent FROM results ORDER BY result_id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [row["score_percent"] for row in reversed(rows)]


def clear_results() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM results")
