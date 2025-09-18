from datetime import date

from celery import Task
from loguru import logger

from settings import celery_app
from modules.collector import AdvertsCollector


class CollectData(Task):
    name = "collect-data"
    time_limit = 60 * 30
    acks_late = True
    
    def run(self, date: date, city_alias: str):
        collector = AdvertsCollector(
            date=date,
            city_alias=city_alias,
        )
        result = collector.run()
        logger.info(f"Data: {result}")


celery_app.register_task(task=CollectData())
