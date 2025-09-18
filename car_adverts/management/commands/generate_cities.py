from loguru import logger
from django.core.management.base import BaseCommand

from car_adverts.models import City
from modules.browser import ChromeBrowser


class Command(BaseCommand):
    def generate(self, *args, **kwargs):
        cities = []
        with ChromeBrowser() as browser:
            cities.extend(browser.get_cities())
        if not cities:
            logger.error("There are no cities")
            return
        objs = []
        for city in cities:
            if not city.get("alias"):
                continue
            objs.append(
                City(title=city.get("label"), alias=city.get("alias"))
            )
        City.objects.bulk_create(
            objs=objs,
            batch_size=100,
            ignore_conflicts=False,
            update_conflicts=False,
        )

    def handle(self, *args, **options):
        logger.info("Begin generate cities")
        self.generate(*args, **options)
        logger.info("Generate cities ended")
