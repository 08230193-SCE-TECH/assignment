"""Application-wide settings.

>>> Change STUDENT_NAME and ROLL_NO before taking your report screenshots. <<<
They appear in the window title and in Help > About.
"""

from pathlib import Path

APP_NAME = "Quiz Master"
STUDENT_NAME = "Your Name"
ROLL_NO = "Your Roll No"
COURSE = "Unit V - Exploring GUI Frameworks (PyQt6)"

# Paths are built from this file's location, so nothing is hard-coded.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "quiz.db"
ASSETS_DIR = BASE_DIR / "assets"      # arrow / checkbox / radio images used by the stylesheet

ALL_CATEGORIES = "All Categories"   # label used in the category drop-down
PASS_PERCENT = 50.0                 # score needed to pass
DEFAULT_SECONDS = 20                # default time allowed per question
MIN_SECONDS = 5
MAX_SECONDS = 60
MAX_QUESTIONS_PER_QUIZ = 20
