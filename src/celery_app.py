import os

from celery import Celery

from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

app = Celery('parser')
app.conf.update(
    broker_url=os.getenv('REDIS_URL'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)

app.conf.beat_schedule = {
    'parse-hourly': {
        'task': 'src.tasks.parse_problems',
        'schedule': crontab(minute=0, hour='*'),  # каждый час
        'args': (1000,),
    },
}

if __name__ == '__main__':
    app.start()
