from celery import Celery
import os

broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery('tasks', broker=broker_url, backend=broker_url)
celery_app.conf.update(
    result_expires=3600,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_rate_limit='100/m',  # Throttling example: 10 tasks per minute
)

# To import the tasks
celery_app.autodiscover_tasks(['utils.email_utils'])
