from celery import Celery
from decouple import config


REDIS_URL = config("REDIS_URL")
app: Celery = Celery(main="proj", broker=REDIS_URL, backend=REDIS_URL)
app.autodiscover_tasks()
app.conf.timezone = "Asia/Almaty"
