from typing import AsyncGenerator
from app.database import SessionLocal
from app.domain.postgres_store import PostgresAppointmentStore
from app.domain.booking import AppointmentStore


async def get_store() -> AsyncGenerator[AppointmentStore, None]:
    """Dependency: returns a Postgres-backed store for the request, cleans up after."""
    session = SessionLocal()
    try:
        yield PostgresAppointmentStore(session)
    finally:
        await session.close()
