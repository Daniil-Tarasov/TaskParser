from celery import Celery
from src.database import SessionLocal
from src.api import CodeforcesAPI
from sqlalchemy import text

app = Celery('parser')


@app.task
def parse_problems(limit=1000, tags=None):
    api = CodeforcesAPI()
    data = api.get_problems(tags, limit)

    if data["status"] != "OK":
        return {"error": "API failed"}

    db = SessionLocal()
    try:
        problem = Problem(
            codeforces_id=f"{contest_id}{problem_data['index']}",
            name=problem_data['name'],
            rating=problem_data.get('rating'),
            solved_count=problem_data.get('solved_count', 0),
            contest_id=contest.id,
            index=problem_data['index']
        )

        for tag in problem_data.get('tags', []):
            tag_obj = ProblemTag(problem=problem, tag=tag)
            db.add(tag_obj)

        db.add(problem)
        db.commit()

        return {"parsed": len(problems)}
    finally:
        db.close()


def save_problem_simple(db, problem_data, statistics):
    """Сохранение БЕЗ тегов"""
    contest_id = problem_data['contestId']
    index = problem_data['index']
    problem_cf_id = f"{contest_id}{index}"

    contest = db.query(Contest).filter_by(codeforces_id=contest_id).first()
    if not contest:
        contest = Contest(codeforces_id=contest_id, name=f"CF{contest_id}")
        db.add(contest)
        db.flush()

    stats = next((s for s in statistics if s['contestId'] == contest_id and s['index'] == index), None)

    existing = db.query(Problem).filter_by(codeforces_id=problem_cf_id).first()
    if not existing:
        problem = Problem(
            codeforces_id=problem_cf_id,
            contest_id=contest.id,
            name=problem_data['name'][:255],
            index=index,
            rating=problem_data.get('rating'),
            solved_count=stats['solvedCount'] if stats else 0
        )
        db.add(problem)
        return 1
    return 0
