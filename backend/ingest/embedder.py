"""Ollama embedding via open-source models."""

import httpx
import os


class OllamaEmbedder:
    """Generate embeddings using Ollama + open-source model."""

    def __init__(
        self,
        base_url: str = None,
        model: str = "nomic-embed-text",
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model
        self._embedding_cache = {}

    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for text via Ollama.

        Args:
            text: Text to embed

        Returns:
            1536-dimensional embedding vector

        Raises:
            ConnectionError: If Ollama is unreachable
        """
        if not text:
            return [0.0] * 1536

        # Check cache
        if text in self._embedding_cache:
            return self._embedding_cache[text]

        url = f"{self.base_url}/api/embed"
        payload = {
            "model": self.model,
            "input": text,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data = response.json()
        embedding = data.get("embeddings", [[]])[0]

        # Cache for next time
        self._embedding_cache[text] = embedding

        return embedding
