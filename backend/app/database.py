import os

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/tari")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
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
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    __table_args__ = (
        UniqueConstraint("office", "date", "time", name="uq_slot"),
        Index("idx_citizen_name", "citizen_name"),
    )


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    source_url = Column(String(512), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    __table_args__ = (Index("idx_embedding", "embedding", postgresql_using="ivfflat"),)


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
