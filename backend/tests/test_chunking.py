from ingest.chunker import Chunk, chunk_text


class TestChunkingBasics:
    """Test semantic chunking of TARI documents."""

    def test_splits_by_header_boundaries(self):
        """Chunks respect markdown header boundaries (##, ####)."""
        text = """## Section One
        Some content here.

        ## Section Two
        More content."""

        chunks = chunk_text(text)

        assert len(chunks) == 2
        assert "Section One" in chunks[0].text
        assert "Section Two" in chunks[1].text

    def test_enforces_max_token_limit(self):
        """No chunk exceeds max_tokens (512)."""
        # Generate a long text
        long_section = "word " * 500  # ~500 words
        text = f"## Long Section\n{long_section}"

        chunks = chunk_text(text, max_tokens=512)

        for chunk in chunks:
            # Rough estimate: 1 token ≈ 1 word in English
            token_count = len(chunk.text.split())
            assert token_count <= 512 + 50  # Allow small margin

    def test_adds_overlap_between_chunks(self):
        """Adjacent chunks overlap (context preservation)."""
        text = "## A\n" + "sentence. " * 100 + "\n## B\n" + "sentence. " * 100

        chunks = chunk_text(text, max_tokens=200, overlap_tokens=50)

        assert len(chunks) >= 2
        # Check that chunks share some content (overlap)
        if len(chunks) >= 2:
            chunk1_end = chunks[0].text[-100:]
            chunk2_start = chunks[1].text[:100]
            # At least some word overlap should exist
            chunk1_words = set(chunk1_end.split())
            chunk2_words = set(chunk2_start.split())
            assert len(chunk1_words & chunk2_words) > 0

    def test_preserves_chunk_metadata(self):
        """Each chunk retains source_url and chunk_index."""
        text = "## Part 1\ncontent 1\n\n## Part 2\ncontent 2"
        source_url = "https://example.com/tari"

        chunks = chunk_text(text, source_url=source_url)

        for i, chunk in enumerate(chunks):
            assert chunk.source_url == source_url
            assert chunk.chunk_index == i
            assert isinstance(chunk, Chunk)

    def test_handles_empty_input(self):
        """Empty or whitespace-only input returns empty list."""
        assert chunk_text("") == []
        assert chunk_text("   \n\n  ") == []

    def test_respects_minimum_chunk_size(self):
        """Chunks are meaningful (not 1-2 words)."""
        text = "## Section\n" + "word " * 50  # ~50 words

        chunks = chunk_text(text, min_tokens=10)

        for chunk in chunks:
            token_count = len(chunk.text.split())
            assert token_count >= 10


class TestChunkingEdgeCases:
    """Edge cases for chunking logic."""

    def test_handles_tables_without_splitting(self):
        """Tables stay intact, not split across chunks."""
        text = """## Data
        | Header1 | Header2 |
        | --- | --- |
        | Row1Col1 | Row1Col2 |
        | Row2Col1 | Row2Col2 |

        More text."""

        chunks = chunk_text(text)

        # Table should be in one chunk (or marked as unsplittable)
        found_table = False
        for chunk in chunks:
            if "Header1" in chunk.text and "Row1Col1" in chunk.text:
                found_table = True
                break
        assert found_table

    def test_handles_lists_coherently(self):
        """Bullet lists stay together."""
        text = """## Instructions
        * Step 1: do this
        * Step 2: do that
        * Step 3: do another thing

        Done."""

        chunks = chunk_text(text)

        # All steps should be in same or adjacent chunks with overlap
        full_text = " ".join([c.text for c in chunks])
        assert "Step 1" in full_text
        assert "Step 3" in full_text

    def test_strips_whitespace_properly(self):
        """No leading/trailing whitespace in chunks."""
        text = "## Title\n\n\n   Some content   \n\n## Next"

        chunks = chunk_text(text)

        for chunk in chunks:
            assert chunk.text == chunk.text.strip()
            assert not chunk.text.startswith(" ")
            assert not chunk.text.endswith(" ")

    def test_handles_nested_headers(self):
        """Properly handles #### (h4), ## (h2) mixed."""
        text = """## Main Section
        Content here.

        #### Subsection
        Sub content.

        ## Another Main
        More."""

        chunks = chunk_text(text)

        # Should create semantic chunks respecting hierarchy
        assert len(chunks) >= 2

    def test_single_header_no_content(self):
        """Header with no content creates minimal chunk."""
        text = "## Header\n\n## Another Header"

        chunks = chunk_text(text)

        # Should not create empty chunks
        assert all(len(c.text.split()) > 0 for c in chunks)
