from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

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

    async def override_get_store():
        yield store

    # Mock the Ollama embedder to avoid requiring running Ollama service
    mock_embed = AsyncMock(return_value=[0.1] * 768)

    # Mock pgvector retrieval to return empty results (allows tests to run without DB)
    mock_retrieve = AsyncMock(return_value=[])

    with patch("app.rag._embedder.embed", mock_embed), \
         patch("app.rag._retrieve_similar", mock_retrieve):
        app.dependency_overrides[get_store] = override_get_store
        yield TestClient(app)
        app.dependency_overrides.clear()
