"""
Run the full TARI corpus ingestion pipeline.

Usage:
  uv run python -m ingest
"""

import asyncio
import json
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingest.pipeline import ingest_json_file
from app.database import Base, DocumentModel


async def main():
    """Load all TARI JSON files → chunk → embed → store in pgvector."""

    # Database setup
    db_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/tari_db"
    engine = create_async_engine(db_url, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Ingest all TARI JSON files
    data_dir = Path(__file__).parent.parent.parent / "data"
    json_files = list(data_dir.glob("tari_*.json"))

    print(f"Found {len(json_files)} TARI files to ingest...")

    total_chunks = 0
    for json_file in sorted(json_files):
        print(f"Processing {json_file.name}...", end=" ", flush=True)

        async with async_session() as session:
            try:
                chunks_added = await ingest_json_file(json_file, session)
                print(f"✓ {chunks_added} chunks")
                total_chunks += chunks_added
            except Exception as e:
                print(f"✗ Error: {e}")

    print(f"\n✓ Ingestion complete: {total_chunks} total chunks indexed")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
