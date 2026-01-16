import os

from celery import Celery

from dotenv import load_dotenv

load_dotenv()

app = Celery('parser')
app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)

if __name__ == '__main__':
    app.start()
