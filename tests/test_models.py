from src.models import Contest, Problem, ProblemTag


def test_create_contest_problem_tags(db_session):
    # Arrange
    contest = Contest(codeforces_id=2185, name="Round 987")
    db_session.add(contest)
    db_session.flush()
    contest = db_session.query(Contest).first()

    # Problem
    problem = Problem(
        codeforces_id="2185A",
        contest_id=contest.id,
        name="Perfect Root",
        rating=1200,
        solved_count=30850,
        index="A"
    )
    db_session.add(problem)
    db_session.flush()

    # Теги
    tag1 = ProblemTag(problem_id=problem.id, tag="math")
    tag2 = ProblemTag(problem_id=problem.id, tag="constructive")
    db_session.add_all([tag1, tag2])
    db_session.commit()

    # Проверяем связи
    problem = db_session.query(Problem).filter(Problem.codeforces_id == "2185A").first()
    assert len(problem.tags) == 2
    assert problem.tags[0].tag == "math"
    assert problem.contest.codeforces_id == 2185


def test_problem_repr(db_session):
    """🔥 ТОЛЬКО СИНХРОННАЯ версия!"""
    problem = Problem(codeforces_id="2191B", name="MEX Reordering", rating=1800)
    db_session.add(problem)
    db_session.flush()

    assert "MEX Reordering" in str(problem)
    assert problem.codeforces_id == "2191B"
