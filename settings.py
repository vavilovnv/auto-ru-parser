import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    CSV_FOLDER_NAME: str = "csv_files"
    URL: str = os.getenv("URL", "")
    COOKIE: str = os.getenv("COOKIE", "")
    HEADERS: dict[str, str] = {
        "user-agent": os.getenv("USER_AGENT", ""),
        "accept": os.getenv("ACCEPT", ""),
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Opera";v="87"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-mode": "no-cors",
        "Cookie": COOKIE,
    }
    OPEN_CSV_FILE: bool = True
    USE_SELENIUM: bool = True
    USE_SELENIUM_IN_BACKGROUND: bool = False


app_settings = Settings()
