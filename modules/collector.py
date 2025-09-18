import time
import random
from datetime import datetime, date

import requests
from bs4 import BeautifulSoup, Tag
from loguru import logger
from fake_useragent import UserAgent

from car_adverts.models import Advert


MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


class AdvertsCollector:
    def __init__(
        self, date: date, city_alias: str, max_attempts: int = 3
    ):
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "referer": "https://kolesa.kz/",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24",\
             "Microsoft Edge";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "x-requested-with": "XMLHttpRequest",
        }
        self.date = date
        self.city = city_alias
        self.max_attempts = max_attempts if max_attempts > 1 else 3
        self.base_url = "https://kolesa.kz/cars/"

    def data_processing(self, content: bytes) -> list:
        soup = BeautifulSoup(markup=content)
        car_list: list[Tag] = soup.find_all(
            name="div",
            attrs={"class": "a-list__item"},
        )
        adverts = []
        breakpoint()
        for item in car_list:
            card = item.find(name="div", attrs={"class": "a-card js__a-card"})
            advert_id: str = card.attrs.get("data-id")
            public_date: str = card.find(
                name="span",
                attrs={"class": "a-card__param--date"},
            )
            try:
                day, month = public_date.get_text().split(" ")
            except Exception as e:
                logger.debug(f"Something went wrong: {e}")
                continue
            date_to_compare = date(
                year=datetime.now().year,
                month=MONTHS.get(month),
                day=int(day),
            )
            if date_to_compare < self.date:
                continue
            adverts.append((int(advert_id), date_to_compare))
        return adverts

    def run(self):
        adverts = []
        page = 1
        no_data_counter = 0
        while True:
            self.headers["user-agent"] = UserAgent().random
            page_arg = "" if page == 1 else f"?page={page}"
            url = f"{self.base_url}{self.city}/{page_arg}"
            try:
                logger.debug(f"Make request url: {url}")
                response = requests.get(url=url, headers=self.headers)
                response.raise_for_status()
            except Exception as e:
                logger.error(f"Something happened: {e}")
                return
            content = response.content
            if not content:
                logger.debug("There are no content")
                continue
            page += 1
            if page > 5:
                break
            data = self.data_processing(content=content)
            if not data:
                no_data_counter += 1
                logger.debug(f"There are no data, counter is {no_data_counter}")
                if no_data_counter > 3:
                    break
            adverts.extend(data)
            delay = random.randint(6, 10)
            logger.debug(f"Sleep for {delay} seconds")
            time.sleep(delay)
        return adverts
