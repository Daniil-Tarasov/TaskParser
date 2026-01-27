from unittest.mock import patch

from src.models import Contest, Problem, ProblemTag
from src.tasks import parse_problems, save_problem_simple


class TestParseProblemsTask:
    """Парсинг"""

    @patch("src.tasks.CodeforcesAPI")
    def test_parse_problems_success(self, mock_api_class, db_session, contest):
        """Успешный парсинг 1 задачи"""

        mock_api = mock_api_class.return_value
        mock_api.get_problems.return_value = {
            "status": "OK",
            "result": [
                {
                    "contestId": 2185,
                    "index": "A",
                    "name": "Perfect Root",
                    "rating": 1200,
                    "solvedCount": 30850,
                    "tags": ["math", "constructive"],
                }
            ],
        }

        with patch("src.tasks.SessionLocal", return_value=db_session):
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

    @patch("src.tasks.CodeforcesAPI")
    def test_parse_problems_api_error(self, mock_api_class, db_session):
        """API FAILED"""

        mock_api = mock_api_class.return_value
        mock_api.get_problems.return_value = {"status": "FAILED"}

        with patch("src.tasks.SessionLocal", return_value=db_session):
            result = parse_problems()

        assert result == {"error": "API failed"}

    @patch("src.tasks.CodeforcesAPI")
    def test_parse_problems_existing_problem(self, mock_api_class, db_session):
        """Skip существующей"""

        contest = Contest(codeforces_id=2185, name="Test")
        db_session.add(contest)
        db_session.flush()

        problem = Problem(codeforces_id="2185A", contest_id=contest.id, name="Existing")
        db_session.add(problem)
        db_session.commit()

        mock_api = mock_api_class.return_value
        mock_api.get_problems.return_value = {
            "status": "OK",
            "result": [{"contestId": 2185, "index": "A", "name": "New"}],
        }

        with patch("src.tasks.SessionLocal", return_value=db_session):
            result = parse_problems(limit=1)

        assert result == {"parsed": 0}
        saved_problem = db_session.query(Problem).filter_by(codeforces_id="2185A").first()
        assert saved_problem.name == "Existing"

    @patch("src.tasks.CodeforcesAPI")
    def test_parse_problems_multiple(self, mock_api_class, db_session):
        """Множественные теги"""

        mock_api = mock_api_class.return_value
        mock_api.get_problems.return_value = {
            "status": "OK",
            "result": [
                {"contestId": 2191, "index": "B", "name": "MEX Reordering", "tags": ["data structures", "greedy"]}
            ],
        }

        with patch("src.tasks.SessionLocal", return_value=db_session):
            result = parse_problems(limit=1)

        assert result == {"parsed": 1}
        problem = db_session.query(Problem).filter_by(codeforces_id="2191B").first()
        tags = db_session.query(ProblemTag).filter_by(problem_id=problem.id).all()
        assert len(tags) == 2


class TestSaveProblemSimple:
    """Сохранение задачи"""

    def test_save_new_problem(self, db_session, contest):
        problem_data = {"contestId": 2185, "index": "A", "name": "Perfect Root"}
        statistics = [{"contestId": 2185, "index": "A", "solvedCount": 30850}]

        count = save_problem_simple(db_session, problem_data, statistics)

        assert count == 1

        contest = db_session.query(Contest).filter_by(codeforces_id=2185).first()
        problem = db_session.query(Problem).filter_by(codeforces_id="2185A").first()

        assert contest is not None, "Contest НЕ создался!"
        assert problem is not None, "Problem НЕ создался!"
        assert contest.codeforces_id == 2185
        assert problem.name == "Perfect Root"
        assert problem.solved_count == 30850

        db_session.rollback()

    def test_save_existing_problem(self, db_session, contest):
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
