import time
from datetime import datetime, date

from playwright.sync_api import sync_playwright
from loguru import logger

from modules.scripts import (
    GET_AREAS,
    GET_ADVERTS_DATES,
    GET_ADVERTS_IDS,
    GET_CHARS,
    GET_DESCR,
    GET_PRICE,
    GET_TITLE,
    GET_YEAR,
    GET_IMAGES,
)


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


class ChromeBrowser:
    def __init__(self, headless: bool = True):
        self.base_url = "https://kolesa.kz/cars/"
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )
        self.page = self.browser.new_page()
        self.page.set_default_timeout(60000)
        logger.info("Browser opened")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed")

    def get_cities(self):
        self.page.goto(url=self.base_url)
        # more_btn = self.page.locator(selector=".FilterGroup__toggle")
        # self.page.evaluate(
        #     expression="window.document.querySelector('.FilterGroup__toggle').click()"
        # )
        btn = self.page.wait_for_selector(selector=".FilterGroup__toggle")
        if btn:
            btn.click()
        else:
            logger.error("Кнопки нет")
        time.sleep(3)
        # temp = self.page.wait_for_selector(selector=".filter-region__item")
        cities_block = self.page.evaluate(expression=GET_AREAS)
        logger.info(f"Cities block: {cities_block}")
        return cities_block

    def get_adverts(self, city_alias: str, parse_date: date):
        data = {}
        page = 1
        while True:
            page_arg = "" if page == 1 else f"?page={page}"
            url = f"{self.base_url}{city_alias}/{page_arg}"
            self.page.goto(url=url)
            ids = self.page.evaluate(expression=GET_ADVERTS_IDS)
            dates = self.page.evaluate(expression=GET_ADVERTS_DATES)
            for i, item in enumerate(ids):
                temp: str = dates[i]
                day, month = temp.split(" ")
                date_to_compare = date(
                    year=datetime.now().year,
                    month=MONTHS.get(month),
                    day=int(day),
                )
                if date_to_compare < parse_date:
                    continue
                data[int(item)] = date_to_compare
            page += 1
            if page > 5:
                break
            time.sleep(5)
        return data

    def run_script(self, expression: str):
        try:
            data = self.page.evaluate(expression=expression)
            return data
        except Exception as e:
            logger.error(f"Cannot execute script: {e}")
            return None

    def get_full_data(self, advert_id: int):
        url = f"https://kolesa.kz/a/show/{advert_id}"
        self.page.goto(url=url)
        title = self.run_script(expression=GET_TITLE)
        year_of_issue = self.run_script(expression=GET_YEAR)
        description = self.run_script(expression=GET_DESCR)
        characteristics = self.run_script(expression=GET_CHARS)
        temp_price: str | None = self.run_script(expression=GET_PRICE)
        price = temp_price.split(" ")[0].replace("\xa0", "")
        return {
            "title": title,
            "year_of_issue": int(year_of_issue),
            "description": description,
            "characteristics": characteristics,
            "price": int(price)
        }

    def collect_links(self, advert_id: int) -> list[str] | None:
        url = f"https://kolesa.kz/a/show/{advert_id}"
        self.page.goto(url=url)
        links = self.run_script(expression=GET_IMAGES)
        return links
