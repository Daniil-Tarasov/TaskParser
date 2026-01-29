import os

from celery import Celery
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.api_client import CodeforcesAPI
from src.database import SessionLocal
from src.models import Contest, Problem, ProblemTag

load_dotenv()
broker = os.getenv("REDIS_URL")
backend = os.getenv("CELERY_RESULT_BACKEND")

app = Celery("parser", broker=broker, backend=backend)


@app.task
def parse_problems(limit=1000, tags=None):
    api = CodeforcesAPI()
    data = api.get_problems(tags, limit)

    if data["status"] != "OK":
        return {"error": "API failed"}

    db: Session = SessionLocal()
    try:
        parsed_count = 0
        for problem_data in data["result"]:
            contest_id = problem_data["contestId"]
            contest = db.query(Contest).filter_by(codeforces_id=contest_id).first()
            if not contest:
                contest = Contest(codeforces_id=contest_id, name=f"CF{contest_id}")
                db.add(contest)
                db.flush()

            problem_cf_id = f"{contest_id}{problem_data['index']}"
            if db.query(Problem).filter_by(codeforces_id=problem_cf_id).first():
                continue

            problem = Problem(
                codeforces_id=problem_cf_id,
                contest_id=contest.id,
                name=problem_data["name"],
                rating=problem_data.get("rating"),
                solved_count=problem_data.get("solvedCount", 0),
                index=problem_data["index"],
            )

            db.add(problem)
            db.flush()

            for tag in problem_data.get("tags", []):
                tag_obj = ProblemTag(problem_id=problem.id, tag=tag)
                db.add(tag_obj)

            parsed_count += 1

        db.commit()
        return {"parsed": parsed_count}
    finally:
        db.close()


def save_problem_simple(db: Session, problem_data, statistics):
    contest_id = problem_data["contestId"]
    index = problem_data["index"]
    problem_cf_id = f"{contest_id}{index}"

    contest = db.query(Contest).filter_by(codeforces_id=contest_id).first()
    if not contest:
        contest = Contest(codeforces_id=contest_id, name=f"CF{contest_id}")
        db.add(contest)
        db.flush()

    stats = next((s for s in statistics if s["contestId"] == contest_id and s["index"] == index), None)

    existing = db.query(Problem).filter_by(codeforces_id=problem_cf_id).first()
    if not existing:
        problem = Problem(
            codeforces_id=problem_cf_id,
            contest_id=contest.id,
            name=problem_data["name"][:255],
            index=index,
            rating=problem_data.get("rating"),
            solved_count=stats["solvedCount"] if stats else 0,
        )
        db.add(problem)
        db.flush()
        return 1
    return 0
