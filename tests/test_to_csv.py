"""Tests for save_to_file."""

import csv
from pathlib import Path

import pytest

from src.schemas import Car
from src.to_csv import app_settings, save_to_file


def test_save_to_file__csv_format(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # -- Arrange --
    monkeypatch.setattr(app_settings, "CSV_FOLDER_NAME", str(tmp_path))
    monkeypatch.setattr(app_settings, "OPEN_CSV_FILE", False)
    cars = [
        Car(description="BMW X5", url="https://auto.ru/1/", price=5_000_000, year=2021)
    ]

    # -- Act --
    save_to_file(cars)

    # -- Assert --
    csv_files = list(tmp_path.glob("*.csv"))
    assert len(csv_files) == 1

    with open(csv_files[0], encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter=";"))

    assert rows[0] == ["Car", "Link", "Price (RUR)", "Year"]
    assert rows[1] == ["BMW X5", "https://auto.ru/1/", "5000000", "2021"]


def test_save_to_file__multiple_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # -- Arrange --
    monkeypatch.setattr(app_settings, "CSV_FOLDER_NAME", str(tmp_path))
    monkeypatch.setattr(app_settings, "OPEN_CSV_FILE", False)
    cars = [
        Car(description="BMW X5", url="https://auto.ru/1/", price=5_000_000, year=2021),
        Car(
            description="Toyota Camry",
            url="https://auto.ru/2/",
            price=2_500_000,
            year=2022,
        ),
    ]

    # -- Act --
    save_to_file(cars)

    # -- Assert --
    csv_files = list(tmp_path.glob("*.csv"))
    with open(csv_files[0], encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter=";"))

    assert len(rows) == 3  # header + 2 cars
    assert rows[1][0] == "BMW X5"
    assert rows[2][0] == "Toyota Camry"


def test_save_to_file__empty_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # -- Arrange --
    monkeypatch.setattr(app_settings, "CSV_FOLDER_NAME", str(tmp_path))
    monkeypatch.setattr(app_settings, "OPEN_CSV_FILE", False)

    # -- Act --
    save_to_file([])

    # -- Assert --
    csv_files = list(tmp_path.glob("*.csv"))
    assert len(csv_files) == 1

    with open(csv_files[0], encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter=";"))

    assert len(rows) == 1  # header only
    assert rows[0] == ["Car", "Link", "Price (RUR)", "Year"]
