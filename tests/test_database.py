from sqlalchemy import text

from src.models import Contest, Problem, ProblemTag


def test_search_problem_by_code(db_session):
    contest = Contest(codeforces_id=2185, name="Round 987")
    db_session.add(contest)
    db_session.flush()

    problem = Problem(
        codeforces_id="2185A",
        contest_id=contest.id,
        name="Perfect Root",
        rating=1200,
        solved_count=30850,
        index="A"
    )
    db_session.add(problem)
    db_session.commit()

    result = db_session.execute(text("""
        SELECT p.codeforces_id, p.name, p.rating, p.solved_count,
               c.name as contest_name
        FROM problems p
        LEFT JOIN contests c ON p.contest_id = c.id
        WHERE UPPER(p.codeforces_id) = :query
        LIMIT 1
    """), [{"query": "2185A"}])

    problem_found = result.fetchone()
    assert problem_found is not None
    assert problem_found.codeforces_id == "2185A"
    assert problem_found.rating == 1200


def test_tag_filter(db_session):
    contest = Contest(codeforces_id=2185, name="Round 987")
    db_session.add(contest)
    db_session.flush()

    problem1 = Problem(codeforces_id="2185A", contest_id=contest.id, name="Math Task", rating=1200)
    problem2 = Problem(codeforces_id="2185B", contest_id=contest.id, name="Graph Task", rating=1800)
    db_session.add_all([problem1, problem2])
    db_session.flush()

    tag_math = ProblemTag(problem_id=problem1.id, tag="math")
    tag_graph = ProblemTag(problem_id=problem2.id, tag="graphs")
    db_session.add_all([tag_math, tag_graph])
    db_session.commit()

    result = db_session.execute(text("""
        SELECT p.codeforces_id, p.name, p.rating, p.solved_count
        FROM problems p
        INNER JOIN problem_tags pt ON p.id = pt.problem_id
        WHERE pt.tag = :tag
        ORDER BY p.rating DESC, p.id
        LIMIT 10
    """), [{"tag": "math"}])

    problems = result.fetchall()
    assert len(problems) == 1
    assert problems[0].codeforces_id == "2185A"
