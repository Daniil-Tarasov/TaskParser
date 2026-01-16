from src.celery_app import app
from src.database import SessionLocal
from src.api_client import CodeforcesAPI
from src.models import Contest, Problem
from sqlalchemy import text


@app.task
def parse_problems(limit: int = 100):
    print("🚀 ПАРСЕР CODEFORCES (БЕЗ ТЕГОВ)")

    api = CodeforcesAPI()
    data = api.get_problems(limit=limit)
    problems = data['result']['problems']
    stats = data['result']['problemStatistics']

    print(f"📥 Получено {len(problems)} задач")

    db = SessionLocal()
    saved = 0
    try:
        for i, problem in enumerate(problems[:20]):  # ← ПЕРВЫЕ 20!
            print(f"💾 [{i + 1}/20] {problem['contestId']}{problem['index']}")

            # БЕЗ ТЕГОВ!
            saved += save_problem_simple(db, problem, stats)

        db.commit()
        print(f"✅ СОХРАНЕНО {saved} НОВЫХ ЗАДАЧ!")
    finally:
        db.close()

    return {"saved": saved, "total": len(problems)}


def save_problem_simple(db, problem_data, statistics):
    """Сохранение БЕЗ тегов"""
    contest_id = problem_data['contestId']
    index = problem_data['index']
    problem_cf_id = f"{contest_id}{index}"

    # Контест
    contest = db.query(Contest).filter_by(codeforces_id=contest_id).first()
    if not contest:
        contest = Contest(codeforces_id=contest_id, name=f"CF{contest_id}")
        db.add(contest)
        db.flush()

    # Статистика
    stats = next((s for s in statistics if s['contestId'] == contest_id and s['index'] == index), None)

    # Задача
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
