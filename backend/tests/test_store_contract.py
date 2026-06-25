"""Behavioral contract shared by every AppointmentStore implementation.

Each test runs against both stores:
  - the in-memory store (fast unit tests, no I/O)
  - the SQLAlchemy-backed store, exercised against an in-process SQLite
    database. SQLite shares Postgres's case-sensitive ``=`` semantics, so the
    SQL query logic this contract pins down (case-insensitive lookup,
    idempotency, double-book prevention) is verified without a running
    database.

This is the regression net that keeps the two implementations from drifting —
the kind of divergence that previously let a production-only lookup bug slip
past the in-memory contract tests.
"""

import pytest
import pytest_asyncio
from app.database import AppointmentModel
from app.domain.booking import AppointmentStore, InMemoryAppointmentStore
from app.domain.postgres_store import PostgresAppointmentStore
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

SLOT = {"office": "tributi", "date": "2099-01-05", "time": "09:00"}
CITIZEN = {"citizen_name": "Mario Rossi", "contact": "+393912345678", "reason": None}


@pytest_asyncio.fixture(params=["inmemory", "sqlalchemy"])
async def store(request):
    if request.param == "inmemory":
        yield InMemoryAppointmentStore()
        return

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: AppointmentModel.__table__.create(sync_conn))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield PostgresAppointmentStore(session)
    await engine.dispose()


def test_both_stores_satisfy_the_protocol():
    assert issubclass(InMemoryAppointmentStore, AppointmentStore)
    assert issubclass(PostgresAppointmentStore, AppointmentStore)


@pytest.mark.asyncio
async def test_book_returns_confirmation(store):
    result = await store.book(**SLOT, **CITIZEN)

    assert result["status"] == "confirmed"
    assert result["confirmation_code"]
    assert result["appointment"]["citizen_name"] == "Mario Rossi"


@pytest.mark.asyncio
async def test_rebooking_same_params_is_idempotent(store):
    first = await store.book(**SLOT, **CITIZEN)
    second = await store.book(**SLOT, **CITIZEN)

    assert second["status"] == "confirmed"
    assert second["confirmation_code"] == first["confirmation_code"]


@pytest.mark.asyncio
async def test_double_book_different_citizen_is_rejected(store):
    await store.book(**SLOT, **CITIZEN)

    result = await store.book(**SLOT, **{**CITIZEN, "citizen_name": "Lucia Bianchi"})

    assert result["status"] == "slot_unavailable"


@pytest.mark.asyncio
async def test_lookup_by_name_is_case_insensitive(store):
    # Stored with original casing ("Mario Rossi"); a lookup in a different case
    # must still resolve — ASR and the agent will not preserve casing.
    await store.book(**SLOT, **CITIZEN)

    result = await store.lookup_by_name("mario rossi")

    assert result["status"] == "found"


@pytest.mark.asyncio
async def test_lookup_unknown_name_returns_not_found(store):
    result = await store.lookup_by_name("Nessuno Esistente")

    assert result["status"] == "not_found"
    assert result["appointment"] is None


@pytest.mark.asyncio
async def test_lookup_filters_by_date(store):
    await store.book(**SLOT, **CITIZEN)

    same_day = await store.lookup_by_name("Mario Rossi", date=SLOT["date"])
    other_day = await store.lookup_by_name("Mario Rossi", date="2099-02-02")

    assert same_day["status"] == "found"
    assert other_day["status"] == "not_found"


@pytest.mark.asyncio
async def test_booked_slots_for_reports_reserved_times(store):
    await store.book(**SLOT, **CITIZEN)

    booked = await store.booked_slots_for(SLOT["office"], SLOT["date"])

    assert SLOT["time"] in booked
