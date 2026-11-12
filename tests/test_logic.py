"""Automated tests for the logic and data layers (no GUI needed).

Run from the project folder:  python -m unittest discover -s tests -v
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
import database
import quiz_logic
from models import Question


def make_questions(n=3):
    return [Question(i, "Test", f"Question number {i}?",
                     ["a", "b", "c", "d"], 1) for i in range(n)]


class QuizLogicTests(unittest.TestCase):

    def test_scoring_and_percent(self):
        session = quiz_logic.QuizSession("Sam", "Test", make_questions(4), 20)
        for choice in (1, 1, 0, None):          # 2 right, 1 wrong, 1 timed out
            session.submit_answer(choice)
        self.assertTrue(session.is_finished)
        self.assertEqual(session.correct_count, 2)
        self.assertEqual(session.percent, 50.0)
        self.assertTrue(session.passed)

    def test_timeout_counts_as_wrong(self):
        session = quiz_logic.QuizSession("Sam", "Test", make_questions(1), 20)
        record = session.submit_answer(None)
        self.assertFalse(record.is_correct)
        self.assertIn("time ran out", record.chosen_text)

    def test_cannot_answer_after_finish(self):
        session = quiz_logic.QuizSession("Sam", "Test", make_questions(1), 20)
        session.submit_answer(1)
        with self.assertRaises(RuntimeError):
            session.submit_answer(1)

    def test_empty_quiz_rejected(self):
        with self.assertRaises(ValueError):
            quiz_logic.QuizSession("Sam", "Test", [], 20)

    def test_grades(self):
        self.assertEqual(quiz_logic.grade_for(100), "A - Excellent")
        self.assertEqual(quiz_logic.grade_for(80), "A - Excellent")
        self.assertEqual(quiz_logic.grade_for(65), "B - Good")
        self.assertEqual(quiz_logic.grade_for(50), "C - Pass")
        self.assertEqual(quiz_logic.grade_for(49.9), "F - Try again")

    def test_feedback_messages(self):
        self.assertIn("Excellent", quiz_logic.feedback_for(90))
        self.assertIn("Good job", quiz_logic.feedback_for(70))
        self.assertIn("passed", quiz_logic.feedback_for(55))
        self.assertIn("try again", quiz_logic.feedback_for(10))

    def test_player_name_validation(self):
        self.assertIsNotNone(quiz_logic.validate_player_name("   "))
        self.assertIsNotNone(quiz_logic.validate_player_name("A"))
        self.assertIsNotNone(quiz_logic.validate_player_name("x" * 31))
        self.assertIsNone(quiz_logic.validate_player_name("Sonam"))

    def test_question_validation(self):
        ok = ("Python", "What is 2 + 2?", ["1", "2", "3", "4"], 3)
        self.assertIsNone(quiz_logic.validate_question_fields(*ok))
        self.assertIsNotNone(quiz_logic.validate_question_fields("", ok[1], ok[2], 3))
        self.assertIsNotNone(quiz_logic.validate_question_fields("P", "Hi", ok[2], 3))
        self.assertIsNotNone(quiz_logic.validate_question_fields("P", ok[1], ["1", "", "3", "4"], 3))
        self.assertIsNotNone(quiz_logic.validate_question_fields("P", ok[1], ["1", "1", "3", "4"], 3))
        self.assertIsNotNone(quiz_logic.validate_question_fields("P", ok[1], ok[2], 7))


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._old_path = config.DB_PATH
        config.DB_PATH = Path(self._tmp.name) / "test.db"
        database.init_db()

    def tearDown(self):
        config.DB_PATH = self._old_path
        self._tmp.cleanup()

    def test_sample_data_seeded_once(self):
        self.assertEqual(database.count_questions(), 15)
        database.init_db()                       # second call must not duplicate
        self.assertEqual(database.count_questions(), 15)
        self.assertEqual(database.get_categories(), ["Bhutan", "Computer Basics", "Python"])
        self.assertEqual(database.count_questions("Python"), 6)

    def test_quiz_question_selection(self):
        questions = database.get_questions_for_quiz("Python", 4, shuffle=False)
        self.assertEqual(len(questions), 4)
        self.assertTrue(all(q.category == "Python" for q in questions))
        everything = database.get_questions_for_quiz(None, 100, shuffle=True)
        self.assertEqual(len(everything), 15)

    def test_add_update_delete_question(self):
        new_id = database.add_question("Maths", "What is 2 + 2?", ["1", "2", "3", "4"], 3)
        self.assertEqual(database.count_questions("Maths"), 1)
        with self.assertRaises(ValueError):      # duplicate text
            database.add_question("Maths", "What is 2 + 2?", ["a", "b", "c", "d"], 0)
        database.update_question(new_id, "Maths", "What is 3 + 3?", ["6", "2", "3", "4"], 0)
        updated = [q for q in database.get_all_questions() if q.question_id == new_id][0]
        self.assertEqual(updated.text, "What is 3 + 3?")
        self.assertEqual(updated.correct_answer, "6")
        database.delete_question(new_id)
        self.assertEqual(database.count_questions("Maths"), 0)
        with self.assertRaises(ValueError):      # already deleted
            database.delete_question(new_id)

    def test_results_summary_filter_and_chart_data(self):
        self.assertEqual(database.get_summary(), (0, 0.0, 0.0))
        database.save_result("Sonam", "Python", 5, 4, 80.0, 20)
        database.save_result("Pema", "Bhutan", 4, 1, 25.0, 15)
        database.save_result("Sonam", "All Categories", 10, 6, 60.0, 20)
        attempts, best, average = database.get_summary()
        self.assertEqual(attempts, 3)
        self.assertEqual(best, 80.0)
        self.assertAlmostEqual(average, (80 + 25 + 60) / 3)
        self.assertEqual(len(database.get_results("")), 3)
        self.assertEqual(len(database.get_results("son")), 2)
        self.assertEqual(database.get_recent_scores(2), [25.0, 60.0])
        database.clear_results()
        self.assertEqual(database.get_summary()[0], 0)


if __name__ == "__main__":
    unittest.main()
