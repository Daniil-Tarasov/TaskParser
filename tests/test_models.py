from src.models import Contest, Problem, ProblemTag


class TestModels:
    """Тесты для моделей"""

    def test_create_contest_problem_tags(self, db_session, contest):
        """Создание моделей"""

        db_session.add(contest)
        db_session.flush()
        contest = db_session.query(Contest).first()

        problem = Problem(
            codeforces_id="2185A",
            contest_id=contest.id,
            name="Perfect Root",
            rating=1200,
            solved_count=30850,
            index="A",
        )
        db_session.add(problem)
        db_session.flush()

        tag1 = ProblemTag(problem_id=problem.id, tag="math")
        tag2 = ProblemTag(problem_id=problem.id, tag="constructive")
        db_session.add_all([tag1, tag2])
        db_session.commit()

        problem = db_session.query(Problem).filter(Problem.codeforces_id == "2185A").first()
        assert len(problem.tags) == 2
        assert problem.tags[0].tag == "math"
        assert problem.contest.codeforces_id == 2185

    def test_problem_repr(self, db_session):
        problem = Problem(codeforces_id="2191B", name="MEX Reordering", rating=1800)
        db_session.add(problem)
        db_session.flush()

        assert "MEX Reordering" in str(problem)
        assert problem.codeforces_id == "2191B"
