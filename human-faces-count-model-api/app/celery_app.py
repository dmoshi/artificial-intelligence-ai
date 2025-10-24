
from celery import Celery
from dotenv import load_dotenv
import os

import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()



# Configure Celery broker and backend (RabbitMQ or Redis)
CELERY_BROKER_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")

celery_app = Celery(
    "face_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,

)

# Optional but recommended:
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(bind=True)
def debug_task(self):
    logger.info(f"Request: {self.request!r}")

# Tell Celery to auto-discover tasks in app.tasks
celery_app.autodiscover_tasks(["app.tasks"])