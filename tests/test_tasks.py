from src.tasks import save_problem_simple
from src.models import Contest, Problem


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
