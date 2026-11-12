# Quiz Master - Quiz App with Timer and Score Report

A desktop quiz application built with **Python 3.10+** and **PyQt6**, storing its data in **SQLite**.
Unit V assignment - Part B (Topic 5.3), project idea 5: *Quiz application with timer and score report*.

## Features
- Choose your name, category, number of questions and **time per question** (slider)
- **Countdown timer** per question with a colour-changing time bar; unanswered questions are skipped when time runs out
- Progress bar, radio-button answers (click them, or press **1-4 / A-D**, then **Enter**), review of every answer with grade, pass/fail and an encouraging message, and a **Try Again** button
- Friendly extras: live name hint, tooltips, hover effects, pointing-hand cursor on clickable controls, confirmation before anything is lost
- **Manage Questions**: add, edit and delete questions (with validation)
- **Score Report**: attempts, best and average score, bar chart of the latest 10 attempts, search by player name, export to CSV, clear history
- Data survives closing and reopening the app (SQLite file in `data/`)

## Install and run

```bash
# 1. open a terminal in this folder (the one that contains main.py)

# 2. create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

# 3. install the dependency
pip install -r requirements.txt

# 4. start the app
python main.py
```

The database `data/quiz.db` is created automatically on first run and filled with 15 sample questions
(Python, Computer Basics, Bhutan). A ready-made copy is already included.

**Before taking screenshots:** open `config.py` and set `STUDENT_NAME` and `ROLL_NO`.
They appear in the window title and in *Help > About*.

**Linux note:** if Qt reports a missing "xcb" plugin, run `sudo apt install libxcb-cursor0`.

## Run the automated tests (logic and database only, no window needed)

```bash
python -m unittest discover -s tests -v
```

## Reset the data
Close the app and delete `data/quiz.db`. It will be recreated with the sample questions next time.

## Project structure

```
main.py              entry point - creates the QApplication and the main window
config.py            settings (name, roll no, paths, time limits)
models.py            Question data class
quiz_logic.py        LOGIC layer: QuizSession (scoring), grades, input validation
database.py          DATA layer: all SQLite queries
ui/                  UI layer
    main_window.py       QMainWindow, menu bar, screen switching, About dialog
    home_page.py         start screen
    quiz_page.py         question screen with QTimer
    result_page.py       score + answer review
    manage_questions.py  add / edit / delete questions dialog
    score_report.py      history, summary, chart, CSV export
    score_chart.py       bar chart drawn with QPainter
    styles.py            Qt stylesheet (QSS)
    helpers.py           message-box and table helpers
tests/test_logic.py  unit tests for the logic and data layers
data/quiz.db         SQLite database with sample data
assets/              small PNG images (dropdown/spin arrows, checkbox and radio indicators) used by the stylesheet
```
