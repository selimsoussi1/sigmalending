from celery import Celery

celery_app = Celery(
    "pdf_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["tasks"],
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  
    result_serializer='json',
    timezone='UTC', # Always good practice to set a timezone
    enable_utc=True,
)

