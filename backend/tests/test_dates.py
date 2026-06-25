from datetime import date

import pytest
from app.domain.dates import parse_iso_date, parse_iso_time, validate_future_date


def test_valid_iso_date_parses():
    d = parse_iso_date("2027-06-15")
    assert d == date(2027, 6, 15)


def test_past_date_rejected():
    d = parse_iso_date("2020-01-01")
    with pytest.raises(ValueError, match="passato"):
        validate_future_date(d)


def test_today_is_not_rejected():
    d = date.today()
    assert validate_future_date(d) == d


def test_non_iso_format_rejected():
    with pytest.raises(ValueError):
        parse_iso_date("15/06/2027")


def test_relative_phrase_rejected():
    with pytest.raises(ValueError):
        parse_iso_date("domani")


def test_empty_string_rejected():
    with pytest.raises(ValueError):
        parse_iso_date("")


def test_valid_time_parses():
    assert parse_iso_time("09:00") == "09:00"
    assert parse_iso_time("12:30") == "12:30"


def test_time_invalid_format_rejected():
    with pytest.raises(ValueError):
        parse_iso_time("9am")


def test_time_out_of_range_rejected():
    with pytest.raises(ValueError):
        parse_iso_time("25:00")
