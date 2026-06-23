import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime, UTC

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://user:password@db:5432/tari")

engine = create_engine(
    DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AppointmentModel(Base):
    __tablename__ = "appointments"

    code = Column(String(16), primary_key=True)
    office = Column(String(255), nullable=False)
    date = Column(String(10), nullable=False)
    time = Column(String(5), nullable=False)
    citizen_name = Column(String(255), nullable=False)
    contact = Column(String(255), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

    __table_args__ = (
        UniqueConstraint("office", "date", "time", name="uq_slot"),
        Index("idx_citizen_name", "citizen_name"),
    )


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Get a database session."""
    return SessionLocal()
