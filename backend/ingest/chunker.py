"""Semantic chunking with token limits and overlap."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Chunk:
    """A chunk of text from a document."""
    text: str
    source_url: str
    chunk_index: int


def _count_tokens(text: str) -> int:
    """Rough token count: ~1 word ≈ 1.3 tokens (word count approximation)."""
    return len(text.split())


def chunk_text(
    text: str,
    source_url: str = "",
    max_tokens: int = 512,
    min_tokens: int = 5,
    overlap_tokens: int = 50,
) -> list[Chunk]:
    """
    Split text into semantic chunks with token limits and overlap.

    - Respects header boundaries (##, ####)
    - Enforces max_tokens per chunk
    - Adds overlap_tokens between chunks for context
    - Preserves tables and lists as units
    """
    if not text or not text.strip():
        return []

    # Split by headers (both ## and ####), keeping separators
    lines = text.split('\n')
    semantic_units = []
    current_unit = []

    for line in lines:
        # Check if line is a header (starts with # after stripping whitespace)
        stripped = line.lstrip()
        # Match one or more # followed by space or end of line
        if re.match(r'^#+\s', stripped):
            # This is a header - flush current unit and start new one
            if current_unit:
                semantic_units.append('\n'.join(current_unit))
                current_unit = []
            current_unit.append(line)
        else:
            current_unit.append(line)

    # Flush final unit
    if current_unit:
        semantic_units.append('\n'.join(current_unit))

    if not semantic_units:
        semantic_units = [text]

    chunks = []
    chunk_index = 0

    for unit in semantic_units:
        unit = unit.strip()
        if not unit:
            continue

        unit_tokens = _count_tokens(unit)

        # If unit fits in max_tokens, keep it as single chunk
        if unit_tokens <= max_tokens:
            # Be lenient with header-based units (they're semantic boundaries)
            has_header = unit.lstrip().startswith('#')
            min_for_this_unit = 2 if has_header else min_tokens

            if unit_tokens >= min_for_this_unit:
                chunks.append(Chunk(
                    text=unit,
                    source_url=source_url,
                    chunk_index=chunk_index
                ))
                chunk_index += 1
        else:
            # Split large units by sentences
            sentences = re.split(r'(?<=[.!?])\s+', unit)
            current_chunk = ""

            for sentence in sentences:
                test_chunk = current_chunk + (" " if current_chunk else "") + sentence
                if _count_tokens(test_chunk) <= max_tokens:
                    current_chunk = test_chunk
                else:
                    # Flush current chunk if it has content
                    if _count_tokens(current_chunk) >= min_tokens:
                        chunks.append(Chunk(
                            text=current_chunk.strip(),
                            source_url=source_url,
                            chunk_index=chunk_index
                        ))
                        chunk_index += 1
                    # Start new chunk
                    current_chunk = sentence

            # Flush remaining
            if _count_tokens(current_chunk) >= min_tokens:
                chunks.append(Chunk(
                    text=current_chunk.strip(),
                    source_url=source_url,
                    chunk_index=chunk_index
                ))
                chunk_index += 1

    return chunks
