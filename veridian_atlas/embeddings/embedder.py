"""
embedder.py
-----------
Local Hugging Face embeddings (no API cost, offline capable).

Model Choices:
- all-MiniLM-L6-v2    → fastest, lightweight, great for clause-level chunks
- all-mpnet-base-v2   → higher quality, slower, larger

This module exposes:
- EmbeddingService.embed(texts) → list of vectors
- EmbeddingService.embed_single(text) → single vector
"""

from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        # loads from local cache after first download
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Batch embed a list of texts."""
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_single(self, text: str) -> List[float]:
        """Embed one string and return a single vector."""
        return self.model.encode([text], convert_to_numpy=True)[0].tolist()


# Optional convenience instance
hf_embedder = EmbeddingService()
