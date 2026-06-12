"""Tests for parse_content and get_pages_amount."""

from src.parser import get_pages_amount, parse_content

NBSP = " "

ITEM_HTML = f"""
<div class="ListingItem__description">
    <div class="ListingItem__summary">Toyota Camry 2.5 AT</div>
    <a class="Link ListingItemTitle__link" href="https://auto.ru/cars/used/sale/123/">Toyota Camry</a>
    <div class="ListingItem__priceBlock">2{NBSP}500{NBSP}000 ₽</div>
    <div class="ListingItem__yearBlock">2022</div>
</div>
"""

PAGINATION_HTML = '<span class="ControlGroup ControlGroup_responsive_no ControlGroup_size_s ListingPagination__pages"><a>1</a><a>2</a><a>3</a></span>'


def test_parse_content__extracts_car_fields() -> None:
    # -- Arrange --
    content = ITEM_HTML.encode("utf-8")

    # -- Act --
    cars = parse_content(content=content)

    # -- Assert --
    assert len(cars) == 1
    car = cars[0]
    assert car.description == "Toyota Camry 2.5 AT"
    assert car.url == "https://auto.ru/cars/used/sale/123/"
    assert car.price == 2_500_000
    assert car.year == 2022


def test_parse_content__handles_missing_fields() -> None:
    # -- Arrange --
    html = '<div class="ListingItem__description"></div>'

    # -- Act --
    cars = parse_content(content=html.encode("utf-8"))

    # -- Assert --
    assert len(cars) == 1
    car = cars[0]
    assert car.description == ""
    assert car.url == ""
    assert car.price == 0
    assert car.year == 0


def test_parse_content__invalid_price_and_year() -> None:
    # -- Arrange --
    html = """
    <div class="ListingItem__description">
        <div class="ListingItem__priceBlock">по договору ₽</div>
        <div class="ListingItem__yearBlock">н/д</div>
    </div>
    """

    # -- Act --
    cars = parse_content(content=html.encode("utf-8"))

    # -- Assert --
    assert len(cars) == 1
    assert cars[0].price == 0
    assert cars[0].year == 0


def test_parse_content__multiple_items() -> None:
    # -- Arrange --
    html = """
    <div class="ListingItem__description">
        <div class="ListingItem__yearBlock">2020</div>
    </div>
    <div class="ListingItem__description">
        <div class="ListingItem__yearBlock">2021</div>
    </div>
    """

    # -- Act --
    cars = parse_content(content=html.encode("utf-8"))

    # -- Assert --
    assert len(cars) == 2
    assert cars[0].year == 2020
    assert cars[1].year == 2021


def test_get_pages_amount__returns_count() -> None:
    # -- Arrange --
    content = PAGINATION_HTML.encode("utf-8")

    # -- Act --
    count = get_pages_amount(content)

    # -- Assert --
    assert count == 3


def test_get_pages_amount__no_pagination() -> None:
    # -- Act --
    count = get_pages_amount(b"<html><body></body></html>")

    # -- Assert --
    assert count == 0
