from unittest.mock import patch

import pytest

from src.tasks import save_problem_simple, parse_problems
from src.models import Contest, Problem, ProblemTag


class TestParseProblemsTask:
    """✅ Celery task parse_problems (EAGER MODE!)"""

    @pytest.mark.usefixtures("db_session")
    @patch('src.tasks.CodeforcesAPI')  # ✅ Правильный путь!
    def test_parse_problems_success(self, mock_api_class, db_session):
        """✅ Успешный парсинг 1 задачи"""
        # Arrange
        mock_api = mock_api_class.return_value
        mock_api.get_problems.return_value = {
            "status": "OK",
            "result": [{
                "contestId": 2185,
                "index": "A",
                "name": "Perfect Root",
                "rating": 1200,
                "solvedCount": 30850,
                "tags": ["math", "constructive"]
            }]
        }

        with patch('src.tasks.SessionLocal', return_value=db_session):
            result = parse_problems(limit=1)

        assert result == {"parsed": 1}

        contest = db_session.query(Contest).filter_by(codeforces_id=2185).first()
        problem = db_session.query(Problem).filter_by(codeforces_id="2185A").first()
        tags = db_session.query(ProblemTag).filter_by(problem_id=problem.id).all()

        assert contest is not None
        assert problem is not None
        assert contest.codeforces_id == 2185
        assert problem.name == "Perfect Root"
        assert problem.rating == 1200
        assert len(tags) == 2

        db_session.rollback()

    @pytest.mark.usefixtures("db_session")
    @patch('src.tasks.CodeforcesAPI')
    def test_parse_problems_api_error(self, mock_api_class, db_session):
        """✅ API FAILED"""
        mock_api = mock_api_class.return_value
        mock_api.get_problems.return_value = {"status": "FAILED"}

        with patch('src.tasks.SessionLocal', return_value=db_session):
            result = parse_problems()

        assert result == {"error": "API failed"}

    @pytest.mark.usefixtures("db_session")
    @patch('src.tasks.CodeforcesAPI')
    def test_parse_problems_existing_problem(self, mock_api_class, db_session):
        """✅ Skip существующей"""
        contest = Contest(codeforces_id=2185, name="Test")
        db_session.add(contest)
        db_session.flush()

        problem = Problem(
            codeforces_id="2185A",
            contest_id=contest.id,
            name="Existing"
        )
        db_session.add(problem)
        db_session.commit()

        mock_api = mock_api_class.return_value
        mock_api.get_problems.return_value = {
            "status": "OK",
            "result": [{"contestId": 2185, "index": "A", "name": "New"}]
        }

        with patch('src.tasks.SessionLocal', return_value=db_session):
            result = parse_problems(limit=1)

        assert result == {"parsed": 0}
        saved_problem = db_session.query(Problem).filter_by(codeforces_id="2185A").first()
        assert saved_problem.name == "Existing"

    @pytest.mark.usefixtures("db_session")
    @patch('src.tasks.CodeforcesAPI')
    def test_parse_problems_multiple(self, mock_api_class, db_session):
        """✅ Множественные теги"""
        mock_api = mock_api_class.return_value
        mock_api.get_problems.return_value = {
            "status": "OK",
            "result": [{
                "contestId": 2191,
                "index": "B",
                "name": "MEX Reordering",
                "tags": ["data structures", "greedy"]
            }]
        }

        with patch('src.tasks.SessionLocal', return_value=db_session):
            result = parse_problems(limit=1)

        assert result == {"parsed": 1}
        problem = db_session.query(Problem).filter_by(codeforces_id="2191B").first()
        tags = db_session.query(ProblemTag).filter_by(problem_id=problem.id).all()
        assert len(tags) == 2


class TestSaveProblemSimple:
    def test_save_new_problem(self, db_session):
        problem_data = {"contestId": 2185, "index": "A", "name": "Perfect Root"}
        statistics = [{"contestId": 2185, "index": "A", "solvedCount": 30850}]

        count = save_problem_simple(db_session, problem_data, statistics)

        assert count == 1

        contest = db_session.query(Contest).filter_by(codeforces_id=2185).first()
        problem = db_session.query(Problem).filter_by(codeforces_id="2185A").first()

        print(f"DEBUG: contest={contest}, problem={problem}")  # Временно!

        assert contest is not None, "Contest НЕ создался!"
        assert problem is not None, "Problem НЕ создался!"
        assert contest.codeforces_id == 2185
        assert problem.name == "Perfect Root"
        assert problem.solved_count == 30850

        db_session.rollback()

    def test_save_existing_problem(self, db_session):
        contest = Contest(codeforces_id=2185, name="Test")
        db_session.add(contest)
        db_session.flush()

        problem = Problem(codeforces_id="2185A", contest_id=contest.id, name="Old")
        db_session.add(problem)
        db_session.commit()

        problem_data = {"contestId": 2185, "index": "A", "name": "New"}
        statistics = [{"contestId": 2185, "index": "A", "solvedCount": 100}]

        count = save_problem_simple(db_session, problem_data, statistics)

        assert count == 0
        problem = db_session.query(Problem).filter_by(codeforces_id="2185A").first()
        assert problem.name == "Old"
        db_session.rollback()
