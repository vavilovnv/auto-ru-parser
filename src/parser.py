"""Parse and process data from the server."""

import random
import time

from bs4 import BeautifulSoup
from requests import Response, get
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from settings import app_settings
from src import strings
from src.schemas import Car

TIME_TO_ENTER_CAPCHA = 25


def get_pages_amount(content: bytes) -> int:
    """Calculate number of pages."""
    soup = BeautifulSoup(content, "html.parser")
    target_data = soup.find(strings.SPAN_TAG, class_=strings.TARGET_CLASS)

    if not target_data:
        return 0

    return len(target_data.contents)


def parse_content(*, content: bytes) -> list[Car]:
    """Parsing page content."""
    cars: list[Car] = []

    soup = BeautifulSoup(content, "html.parser")
    items = soup.find_all(strings.DIV_TAG, class_="ListingItem__description")

    for item in items:
        car_data = ""
        if car_content := item.find(strings.DIV_TAG, strings.ITEM_SUMMARY):
            car_data = car_content.get_text()

        a_tag = item.find(strings.A_TAG, strings.ITEM_TITLE_LINK)
        url = a_tag.get(strings.HREF_TAG, "") if a_tag else ""

        car_price = 0
        if price_content := item.find(strings.DIV_TAG, strings.ITEM_PRICE_CONTENT):
            raw_price = price_content.get_text()
            price_data = raw_price.replace(strings.NBSP_CODE, "").split(strings.RUR)
            if len(price_data):
                try:
                    car_price = int(price_data[0])
                except ValueError:
                    car_price = 0

        prod_year = 0
        if year_data := item.find(strings.DIV_TAG, strings.ITEM_YEAR):
            try:
                prod_year = int(year_data.get_text())
            except ValueError:
                prod_year = 0

        cars.append(
            Car(
                description=car_data,
                url=url,
                price=car_price,
                year=prod_year,
            )
        )

    return cars


def get_html(url: str, headers: dict, params: dict | None = None) -> Response:
    """Get the response from the server."""
    try:
        return get(url, headers=headers, params=params)
    except Exception as error:
        raise ConnectionError(f"При выполнении запроса произошла ошибка: {error}")


def get_html_with_selenium(url: str, params: dict | None = None) -> str | None:
    """Get HTML content using Selenium for better anti-bot protection bypass."""
    service = Service()
    options = Options()

    if app_settings.USE_SELENIUM_IN_BACKGROUND:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={app_settings.HEADERS['user-agent']}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    try:
        full_url = url
        if params:
            full_url += "?" if "?" not in full_url else "&"
            full_url += "&".join([f"{k}={v}" for k, v in params.items()])

        if app_settings.COOKIE:
            driver.execute_cdp_cmd("Network.enable", {})
            cookies = []
            for cookie_str in app_settings.COOKIE.split(";"):
                if "=" in cookie_str:
                    name, value = cookie_str.strip().split("=", 1)
                    cookies.append(
                        {"name": name.strip(), "value": value, "domain": ".auto.ru", "path": "/"}
                    )
            driver.execute_cdp_cmd("Network.setCookies", {"cookies": cookies})

        driver.get(full_url)

        time.sleep(TIME_TO_ENTER_CAPCHA)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")

        time.sleep(random.uniform(1, 3))

        return driver.page_source

    except Exception as exc:
        print(f"Ошибка при использовании Selenium: {exc}")
        return None

    finally:
        driver.quit()


def parse_response(url: str) -> list[Car] | None:
    """Parse the request."""
    url = url or app_settings.URL
    if not url:
        print("URL не указан. Укажите URL или задайте переменную URL в .env")
        return None

    if app_settings.USE_SELENIUM:
        cars = parse_response_with_selenium(url)
    else:
        cars = simple_parse_response(url)

    if not cars:
        return None

    print(f"Получены данные по {len(cars)} авто.")

    return sorted(cars, key=lambda car: int(car.price), reverse=True)


def simple_parse_response(url: str) -> list[Car] | None:
    html = get_html(url, app_settings.HEADERS)
    if html.status_code != 200:
        print(f"Сайт вернул статус-код {html.status_code}")
        return None

    if "captcha" in html.text.lower():
        print(
            "Обнаружена капча! 🤬 \n"
            "Попробуйте обойти капчу и получить данные при помощи Selenium, "
            "для этого нужно запустить парсер с переменной 'USE_SELENIUM=True'. "
        )
        return None

    cars: list[Car] = []
    pages_amount = get_pages_amount(html.content)
    cars.extend(parse_content(content=html.content))

    for page in range(2, pages_amount + 1):
        print(f"Парсим {page} страницу из {pages_amount}...")

        html = get_html(url, app_settings.HEADERS, params={"page": page})
        cars.extend(parse_content(content=html.content))

    return cars


def parse_response_with_selenium(url: str) -> list[Car] | None:
    html_content = get_html_with_selenium(url)

    if not html_content:
        print("Не удалось получить содержимое страницы.")
        return None

    if "captcha" in html_content.lower():
        print("Снова капча! 🤬")
        return None

    html_bytes = html_content.encode("utf-8")

    cars: list[Car] = []
    pages_amount = get_pages_amount(html_bytes)

    if pages_amount == 0:
        print(
            "Не удалось определить количество страниц. \n"
            "Возможно, результат одностраничный или структура сайта изменилась."
        )

    cars.extend(parse_content(content=html_bytes))

    for page in range(2, pages_amount + 1):
        print(f"Парсим {page} страницу из {pages_amount}...")

        # Добавляем случайную задержку между запросами для имитации поведения человека
        sleep_time = random.uniform(3, 7)
        print(f"Ожидание {sleep_time:.2f} секунд перед следующим запросом...")
        time.sleep(sleep_time)

        page_html = get_html_with_selenium(url, params={"page": page})

        if not page_html:
            print(f"Не удалось получить страницу {page}")
            continue

        if "captcha" in page_html.lower():
            print(f"Обнаружена капча на странице {page}! Пропускаем...")
            continue

        page_html_bytes = page_html.encode("utf-8")
        cars.extend(parse_content(content=page_html_bytes))

    return cars
