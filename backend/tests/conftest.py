from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.domain.booking import AppointmentStore
from app.store import get_store


def _next_weekday(min_days_ahead: int = 7) -> str:
    d = date.today() + timedelta(days=min_days_ahead)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d.isoformat()


def _next_saturday(min_days_ahead: int = 7) -> str:
    d = date.today() + timedelta(days=min_days_ahead)
    while d.weekday() != 5:
        d += timedelta(days=1)
    return d.isoformat()


FUTURE_WEEKDAY = _next_weekday()
FUTURE_SATURDAY = _next_saturday()
PAST_DATE = "2020-01-01"


@pytest.fixture
def client():
    store = AppointmentStore()
    app.dependency_overrides[get_store] = lambda: store
    yield TestClient(app)
    app.dependency_overrides.clear()
