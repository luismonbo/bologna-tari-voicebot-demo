"""Contract tests for the four tool HTTP endpoints."""
from tests.conftest import FUTURE_WEEKDAY, FUTURE_SATURDAY, PAST_DATE

VALID_BOOKING = {
    "office": "tributi",
    "date": FUTURE_WEEKDAY,
    "time": "09:00",
    "citizen_name": "Mario Rossi",
    "contact": "mario@example.com",
    "reason": "Chiarimenti TARI",
}


# ---------------------------------------------------------------------------
# POST /tools/query_services
# ---------------------------------------------------------------------------

def test_query_services_returns_context_for_known_topic(client):
    r = client.post("/tools/query_services", json={"question": "Come si paga la TARI?"})
    assert r.status_code == 200
    body = r.json()
    assert "context" in body
    assert "chunks" in body
    assert isinstance(body["chunks"], list)


def test_query_services_context_is_string(client):
    r = client.post("/tools/query_services", json={"question": "Cosa è la TARI?"})
    assert r.status_code == 200
    assert isinstance(r.json()["context"], str)


def test_query_services_unknown_question_returns_empty_context(client):
    r = client.post("/tools/query_services", json={"question": "xyzzy nonsense 1234"})
    assert r.status_code == 200
    body = r.json()
    assert body["context"] == ""
    assert body["chunks"] == []


def test_query_services_missing_question_returns_422(client):
    r = client.post("/tools/query_services", json={})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# POST /tools/check_availability
# ---------------------------------------------------------------------------

def test_check_availability_weekday_returns_slots(client):
    r = client.post("/tools/check_availability", json={"office": "tributi", "date": FUTURE_WEEKDAY})
    assert r.status_code == 200
    body = r.json()
    assert body["date"] == FUTURE_WEEKDAY
    assert body["available"] is True
    assert len(body["slots"]) > 0


def test_check_availability_weekend_returns_unavailable(client):
    r = client.post("/tools/check_availability", json={"office": "tributi", "date": FUTURE_SATURDAY})
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is False
    assert body["slots"] == []


def test_check_availability_past_date_returns_422(client):
    r = client.post("/tools/check_availability", json={"office": "tributi", "date": PAST_DATE})
    assert r.status_code == 422


def test_check_availability_invalid_date_format_returns_422(client):
    r = client.post("/tools/check_availability", json={"office": "tributi", "date": "domani"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# POST /tools/create_appointment
# ---------------------------------------------------------------------------

def test_create_appointment_happy_path(client):
    r = client.post("/tools/create_appointment", json=VALID_BOOKING)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "confirmed"
    assert "confirmation_code" in body
    assert len(body["confirmation_code"]) == 16
    assert "appointment" in body


def test_create_appointment_idempotent_same_code(client):
    r1 = client.post("/tools/create_appointment", json=VALID_BOOKING)
    r2 = client.post("/tools/create_appointment", json=VALID_BOOKING)
    assert r1.json()["confirmation_code"] == r2.json()["confirmation_code"]


def test_create_appointment_double_book_returns_slot_unavailable(client):
    client.post("/tools/create_appointment", json=VALID_BOOKING)
    other = {**VALID_BOOKING, "citizen_name": "Lucia Bianchi", "contact": "lucia@example.com"}
    r = client.post("/tools/create_appointment", json=other)
    assert r.status_code == 200
    assert r.json()["status"] == "slot_unavailable"


def test_create_appointment_past_date_returns_422(client):
    bad = {**VALID_BOOKING, "date": PAST_DATE}
    r = client.post("/tools/create_appointment", json=bad)
    assert r.status_code == 422


def test_create_appointment_invalid_time_format_returns_422(client):
    bad = {**VALID_BOOKING, "time": "9am"}
    r = client.post("/tools/create_appointment", json=bad)
    assert r.status_code == 422


def test_create_appointment_missing_field_returns_422(client):
    bad = {k: v for k, v in VALID_BOOKING.items() if k != "citizen_name"}
    r = client.post("/tools/create_appointment", json=bad)
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# POST /tools/lookup_appointment
# ---------------------------------------------------------------------------

def test_lookup_by_name_found(client):
    client.post("/tools/create_appointment", json=VALID_BOOKING)
    r = client.post("/tools/lookup_appointment", json={"citizen_name": VALID_BOOKING["citizen_name"]})
    assert r.status_code == 200
    assert r.json()["status"] == "found"


def test_lookup_by_name_not_found(client):
    r = client.post("/tools/lookup_appointment", json={"citizen_name": "Nessuno Esistente"})
    assert r.status_code == 200
    assert r.json()["status"] == "not_found"


def test_lookup_empty_request_returns_422(client):
    r = client.post("/tools/lookup_appointment", json={})
    assert r.status_code == 422
