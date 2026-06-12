"""Save data to csv file."""

import csv
import os
import platform
import subprocess
from datetime import datetime

from settings import app_settings
from src import strings
from src.enums import Platform

DATA_FORMAT = "%Y-%m-%d_%H-%M-%S"


def save_to_file(data) -> None:
    """Save data to file."""
    file_path = _get_file_name()

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        w = csv.writer(file, delimiter=";")
        w.writerow(
            [
                strings.CAR_COLUMN_TITLE,
                strings.LINK_COLUMN_TITLE,
                strings.PRICE_COLUMN_TITLE,
                strings.PROD_YEAR_COLUMN_TITLE,
            ]
        )

        for car in data:
            w.writerow([car.description, car.url, car.price, car.year])

    if app_settings.OPEN_CSV_FILE:
        _open_csv_file(file_path)


def _get_file_name() -> str:
    """Get file name."""
    directory = os.path.join(os.getcwd(), app_settings.CSV_FOLDER_NAME)
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = strings.CSV_FILE_NAME.format(
        current_data=datetime.now().strftime(DATA_FORMAT)
    )

    return os.path.join(directory, filename)


def _open_csv_file(file_path: str) -> None:
    """Open csv file."""
    match platform.system():
        case Platform.WINDOWS:
            os.startfile(file_path)
        case Platform.DARWIN:
            subprocess.run(["open", file_path])
        case Platform.LINUX:
            subprocess.run(["xdg-open", file_path])
