import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🔍 Загрузка app...")
from src.celery_app import app

print("🔍 Регистрация задач...")
print("Доступные задачи:", list(app.tasks.keys()))

import src.tasks
print("✅ Tasks импортированы")
print("Итого задач:", len(app.tasks))

if __name__ == '__main__':
    app.worker_main(['worker', '--pool=solo', '--loglevel=DEBUG'])
