import time

from loguru import logger
from django.core.management.base import BaseCommand

from modules.browser import ChromeBrowser
from car_adverts.models import Advert


class Command(BaseCommand):
    def processing(self, advert_id: int):
        with ChromeBrowser() as browser:
            data = browser.get_full_data(advert_id=advert_id)
        return data

    def handle(self, *args, **options):
        adverts = Advert.objects.filter(title__isnull=True)
        if not adverts:
            logger.info("There are no adverts to processing")
            return
        logger.info(f"Founded {len(adverts)} adverts")
        items = []
        fields = []
        for advert in adverts:
            time.sleep(5)
            data = self.processing(advert_id=advert.pk)
            if not data:
                continue
            for key, value in data.items():
                setattr(advert, key, value)
            if not fields:
                for key in data.keys():
                    fields.append(key)
            items.append(advert)
        logger.info(f"Fields for update: {','.join(fields)}")
        Advert.objects.bulk_update(objs=items, fields=fields)
