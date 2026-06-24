import pytest

from app.domain.booking import AppointmentStore, make_idempotency_key
from tests.conftest import FUTURE_WEEKDAY

SLOT = {"office": "tributi", "date": FUTURE_WEEKDAY, "time": "09:00"}
CITIZEN = {"citizen_name": "Mario Rossi", "contact": "mario@example.com", "reason": None}


def test_idempotency_key_is_deterministic():
    key1 = make_idempotency_key("tributi", FUTURE_WEEKDAY, "09:00", "Mario Rossi")
    key2 = make_idempotency_key("tributi", FUTURE_WEEKDAY, "09:00", "Mario Rossi")
    assert key1 == key2


def test_idempotency_key_is_16_chars():
    key = make_idempotency_key("tributi", FUTURE_WEEKDAY, "09:00", "Mario Rossi")
    assert len(key) == 16


def test_different_params_produce_different_keys():
    key1 = make_idempotency_key("tributi", FUTURE_WEEKDAY, "09:00", "Mario Rossi")
    key2 = make_idempotency_key("tributi", FUTURE_WEEKDAY, "09:30", "Mario Rossi")
    assert key1 != key2


def test_happy_path_booking_confirmed():
    store = AppointmentStore()
    result = store.book(**SLOT, **CITIZEN)
    assert result["status"] == "confirmed"
    assert "confirmation_code" in result
    assert "appointment" in result


def test_confirmation_code_matches_idempotency_key():
    store = AppointmentStore()
    result = store.book(**SLOT, **CITIZEN)
    expected = make_idempotency_key(SLOT["office"], SLOT["date"], SLOT["time"], CITIZEN["citizen_name"])
    assert result["confirmation_code"] == expected


def test_same_params_returns_same_code():
    store = AppointmentStore()
    result1 = store.book(**SLOT, **CITIZEN)
    result2 = store.book(**SLOT, **CITIZEN)
    assert result1["confirmation_code"] == result2["confirmation_code"]
    assert result1["status"] == result2["status"] == "confirmed"


def test_double_book_different_citizen_returns_slot_unavailable():
    store = AppointmentStore()
    store.book(**SLOT, **CITIZEN)
    other = {**CITIZEN, "citizen_name": "Lucia Bianchi"}
    result = store.book(**SLOT, **other)
    assert result["status"] == "slot_unavailable"


@pytest.mark.asyncio
async def test_booked_slots_for_returns_reserved_times():
    store = AppointmentStore()
    store.book(**SLOT, **CITIZEN)
    booked = await store.booked_slots_for(SLOT["office"], SLOT["date"])
    assert SLOT["time"] in booked


def test_lookup_by_code_found():
    store = AppointmentStore()
    result = store.book(**SLOT, **CITIZEN)
    code = result["confirmation_code"]
    lookup = store.lookup_by_code(code)
    assert lookup["status"] == "found"
    assert lookup["appointment"]["confirmation_code"] == code


def test_lookup_by_code_not_found():
    store = AppointmentStore()
    lookup = store.lookup_by_code("nonexistent")
    assert lookup["status"] == "not_found"
    assert lookup["appointment"] is None


def test_lookup_by_name_found():
    store = AppointmentStore()
    store.book(**SLOT, **CITIZEN)
    lookup = store.lookup_by_name(CITIZEN["citizen_name"])
    assert lookup["status"] == "found"


def test_lookup_by_name_not_found():
    store = AppointmentStore()
    lookup = store.lookup_by_name("Nessuno Esistente")
    assert lookup["status"] == "not_found"


def test_lookup_by_name_and_date():
    store = AppointmentStore()
    store.book(**SLOT, **CITIZEN)
    lookup = store.lookup_by_name(CITIZEN["citizen_name"], date=SLOT["date"])
    assert lookup["status"] == "found"
