import pytest

from app.domain.availability import check_availability, get_available_slots
from tests.conftest import FUTURE_WEEKDAY, FUTURE_SATURDAY, PAST_DATE
from datetime import date


def test_weekday_returns_slots():
    slots = get_available_slots("tributi", date.fromisoformat(FUTURE_WEEKDAY))
    assert len(slots) > 0


def test_saturday_returns_no_slots():
    slots = get_available_slots("tributi", date.fromisoformat(FUTURE_SATURDAY))
    assert slots == []


def test_slots_are_valid_hhmm_format():
    slots = get_available_slots("tributi", date.fromisoformat(FUTURE_WEEKDAY))
    for slot in slots:
        assert len(slot) == 5
        assert slot[2] == ":"


def test_unknown_office_returns_no_slots():
    slots = get_available_slots("unknown_office", date.fromisoformat(FUTURE_WEEKDAY))
    assert slots == []


def test_check_availability_returns_correct_shape():
    result = check_availability("tributi", FUTURE_WEEKDAY, booked_slots=set())
    assert "date" in result
    assert "available" in result
    assert "slots" in result
    assert result["date"] == FUTURE_WEEKDAY


def test_check_availability_weekday_is_available():
    result = check_availability("tributi", FUTURE_WEEKDAY, booked_slots=set())
    assert result["available"] is True
    assert len(result["slots"]) > 0


def test_check_availability_weekend_is_not_available():
    result = check_availability("tributi", FUTURE_SATURDAY, booked_slots=set())
    assert result["available"] is False
    assert result["slots"] == []


def test_booked_slot_excluded_from_available():
    all_slots = get_available_slots("tributi", date.fromisoformat(FUTURE_WEEKDAY))
    first_slot = all_slots[0]
    result = check_availability("tributi", FUTURE_WEEKDAY, booked_slots={first_slot})
    assert first_slot not in result["slots"]


def test_all_slots_booked_returns_not_available():
    all_slots = get_available_slots("tributi", date.fromisoformat(FUTURE_WEEKDAY))
    result = check_availability("tributi", FUTURE_WEEKDAY, booked_slots=set(all_slots))
    assert result["available"] is False
    assert result["slots"] == []


def test_past_date_raises():
    with pytest.raises(ValueError, match="passato"):
        check_availability("tributi", PAST_DATE, booked_slots=set())
