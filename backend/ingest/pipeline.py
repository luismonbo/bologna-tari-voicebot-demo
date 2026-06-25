"""End-to-end ingestion pipeline: load JSON → chunk → embed → store."""

import json
from pathlib import Path

from app.database import DocumentModel
from sqlalchemy.ext.asyncio import AsyncSession

from ingest.chunker import chunk_text
from ingest.embedder import OllamaEmbedder


async def ingest_json_file(
    file_path: Path,
    session: AsyncSession,
    embedder: OllamaEmbedder = None,
) -> int:
    """
    Ingest a single TARI JSON file: load → chunk → embed → store.

    Args:
        file_path: Path to JSON file with 'source_url' and 'content' keys
        session: SQLAlchemy async session
        embedder: Optional OllamaEmbedder instance (default: create new)

    Returns:
        Number of chunks inserted

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is invalid JSON
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Load JSON
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    source_url = data.get("source_url", "")
    content_data = data.get("content", "")

    # Handle nested content structure (content.content)
    if isinstance(content_data, dict):
        content = content_data.get("content", "")
    else:
        content = content_data

    if not content:
        return 0

    # Initialize embedder if not provided
    if embedder is None:
        embedder = OllamaEmbedder()

    # Chunk
    chunks = chunk_text(content, source_url=source_url)

    # Embed and store
    for chunk in chunks:
        embedding = await embedder.embed(chunk.text)

        doc = DocumentModel(
            source_url=chunk.source_url,
            chunk_text=chunk.text,
            embedding=embedding,
        )
        session.add(doc)

    # Commit
    await session.commit()

    return len(chunks)
