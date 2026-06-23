from typing import Generator
from app.database import SessionLocal
from app.domain.postgres_store import PostgresAppointmentStore
from app.domain.booking import AppointmentStore


def get_store() -> Generator[AppointmentStore, None, None]:
    """Dependency: returns a Postgres-backed store for the request, cleans up after."""
    session = SessionLocal()
    try:
        yield PostgresAppointmentStore(session)
    finally:
        session.close()
