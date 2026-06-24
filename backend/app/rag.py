"""RAG retrieval via pgvector similarity search."""

from sqlalchemy import select

from app.database import DocumentModel, SessionLocal
from ingest.embedder import OllamaEmbedder


_embedder = OllamaEmbedder()


async def _embed_question(question: str) -> list[float]:
    """Embed a user question using Ollama."""
    return await _embedder.embed(question)


async def _retrieve_similar(
    embedding: list[float],
    top_k: int = 3,
) -> list[dict]:
    """
    Retrieve top-K similar documents via pgvector cosine similarity.

    Cosine distance is computed via the <=> operator in pgvector.
    We order by distance ascending to get highest similarity first.
    """
    session = SessionLocal()
    try:
        stmt = (
            select(
                DocumentModel.chunk_text,
                DocumentModel.source_url,
                (1 - (DocumentModel.embedding.cosine_distance(embedding)))
                .label("similarity"),
            )
            .order_by(
                DocumentModel.embedding.cosine_distance(embedding).asc()
            )
            .limit(top_k)
        )

        result = await session.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "text": row.chunk_text,
                "source_url": row.source_url,
                "score": round(float(row.similarity), 4),
            }
            for row in rows
        ]
    finally:
        await session.close()


async def query(question: str, top_k: int = 3, min_similarity: float = 0.5) -> dict:
    """
    Query TARI knowledge base via pgvector similarity search.

    Args:
        question: User question in Italian
        top_k: Number of top results to return
        min_similarity: Minimum cosine similarity score (0-1) to include a result

    Returns:
        dict with "context" (joined text) and "chunks" (list of results)
    """
    embedding = await _embed_question(question)
    chunks = await _retrieve_similar(embedding, top_k)
    relevant = [c for c in chunks if c["score"] >= min_similarity]
    context = "\n\n".join(c["text"] for c in relevant)
    return {"context": context, "chunks": relevant}
