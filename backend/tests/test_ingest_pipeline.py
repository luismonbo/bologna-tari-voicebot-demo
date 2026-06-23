import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from ingest.pipeline import ingest_json_file
from app.database import DocumentModel


@pytest.fixture
def sample_tari_json(tmp_path):
    """Create a sample TARI JSON file for testing."""
    data = {
        "source_url": "https://example.com/tari",
        "content": """## TARI Information
        This is basic TARI information.

        #### How to apply
        1. Step 1
        2. Step 2
        3. Step 3

        ## Payment Methods
        You can pay online or in person."""
    }
    json_file = tmp_path / "test_tari.json"
    json_file.write_text(json.dumps(data))
    return json_file


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


class TestIngestPipeline:
    """Test the full ingestion pipeline: load → chunk → embed → store."""

    @pytest.mark.asyncio
    async def test_loads_json_file(self, sample_tari_json, mock_db_session):
        """Pipeline loads JSON file correctly."""
        with patch("ingest.pipeline.chunk_text") as mock_chunk, \
             patch("ingest.pipeline.OllamaEmbedder") as mock_embedder_class:

            mock_chunk.return_value = []
            mock_db_session.add = MagicMock()

            await ingest_json_file(sample_tari_json, mock_db_session)

            # Should have loaded and parsed the file
            assert mock_chunk.called

    @pytest.mark.asyncio
    async def test_chunks_content(self, sample_tari_json, mock_db_session):
        """Pipeline chunks the content."""
        with patch("ingest.pipeline.chunk_text") as mock_chunk, \
             patch("ingest.pipeline.OllamaEmbedder") as mock_embedder_class:

            mock_chunk.return_value = []
            mock_db_session.add = MagicMock()

            await ingest_json_file(sample_tari_json, mock_db_session)

            # Chunking should be called with the content
            mock_chunk.assert_called_once()

    @pytest.mark.asyncio
    async def test_embeds_each_chunk(self, sample_tari_json, mock_db_session):
        """Pipeline embeds each chunk via Ollama."""
        from ingest.chunker import Chunk

        chunks = [
            Chunk(text="TARI Info", source_url="https://example.com", chunk_index=0),
            Chunk(text="Payment Methods", source_url="https://example.com", chunk_index=1),
        ]

        with patch("ingest.pipeline.chunk_text") as mock_chunk, \
             patch("ingest.pipeline.OllamaEmbedder") as mock_embedder_class:

            mock_chunk.return_value = chunks
            mock_embedder = AsyncMock()
            mock_embedder.embed = AsyncMock(return_value=[0.1] * 1536)
            mock_embedder_class.return_value = mock_embedder
            mock_db_session.add = MagicMock()

            await ingest_json_file(sample_tari_json, mock_db_session)

            # Should embed each chunk
            assert mock_embedder.embed.call_count == len(chunks)

    @pytest.mark.asyncio
    async def test_stores_documents_in_db(self, sample_tari_json, mock_db_session):
        """Pipeline stores DocumentModel records in database."""
        from ingest.chunker import Chunk

        chunks = [
            Chunk(text="Test chunk", source_url="https://example.com", chunk_index=0),
        ]

        with patch("ingest.pipeline.chunk_text") as mock_chunk, \
             patch("ingest.pipeline.OllamaEmbedder") as mock_embedder_class:

            mock_chunk.return_value = chunks
            mock_embedder = AsyncMock()
            mock_embedder.embed = AsyncMock(return_value=[0.1] * 1536)
            mock_embedder_class.return_value = mock_embedder

            added_docs = []
            def capture_add(doc):
                added_docs.append(doc)
            mock_db_session.add = capture_add

            await ingest_json_file(sample_tari_json, mock_db_session)

            # Should have added documents
            assert len(added_docs) == len(chunks)
            # Each should be a DocumentModel
            for doc in added_docs:
                assert hasattr(doc, "chunk_text")
                assert hasattr(doc, "embedding")
                assert hasattr(doc, "source_url")

    @pytest.mark.asyncio
    async def test_commits_to_database(self, sample_tari_json, mock_db_session):
        """Pipeline commits all changes to database."""
        with patch("ingest.pipeline.chunk_text") as mock_chunk, \
             patch("ingest.pipeline.OllamaEmbedder") as mock_embedder_class:

            mock_chunk.return_value = []
            mock_embedder_class.return_value = AsyncMock()

            await ingest_json_file(sample_tari_json, mock_db_session)

            # Should commit
            assert mock_db_session.commit.called

    @pytest.mark.asyncio
    async def test_handles_missing_file(self, mock_db_session):
        """Pipeline raises error for missing file."""
        missing_file = Path("/nonexistent/file.json")

        with pytest.raises(FileNotFoundError):
            await ingest_json_file(missing_file, mock_db_session)

    @pytest.mark.asyncio
    async def test_handles_invalid_json(self, tmp_path, mock_db_session):
        """Pipeline raises error for invalid JSON."""
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            await ingest_json_file(bad_json, mock_db_session)

    @pytest.mark.asyncio
    async def test_pipeline_end_to_end(self, sample_tari_json, mock_db_session):
        """Full pipeline: load → chunk → embed → store."""
        from ingest.chunker import Chunk

        chunks = [
            Chunk(text="Content 1", source_url="https://example.com", chunk_index=0),
            Chunk(text="Content 2", source_url="https://example.com", chunk_index=1),
        ]

        with patch("ingest.pipeline.chunk_text") as mock_chunk, \
             patch("ingest.pipeline.OllamaEmbedder") as mock_embedder_class:

            mock_chunk.return_value = chunks
            mock_embedder = AsyncMock()
            embeddings = [[0.1 * i] * 1536 for i in range(len(chunks))]
            mock_embedder.embed = AsyncMock(side_effect=embeddings)
            mock_embedder_class.return_value = mock_embedder

            added_docs = []
            mock_db_session.add = lambda doc: added_docs.append(doc)

            await ingest_json_file(sample_tari_json, mock_db_session)

            # Verify complete flow
            assert mock_chunk.called
            assert mock_embedder.embed.call_count == len(chunks)
            assert len(added_docs) == len(chunks)
            assert mock_db_session.commit.called
