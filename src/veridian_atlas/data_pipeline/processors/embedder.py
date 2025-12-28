"""
embedder.py
-----------
Local Hugging Face embedding service with GPU/MPS/CPU auto-detection.
"""

from typing import List
import torch
from sentence_transformers import SentenceTransformer

EMBEDDING_MODELS = {
    # "fast": "sentence-transformers/all-MiniLM-L6-v2",
    "balanced": "sentence-transformers/all-mpnet-base-v2",
    "high_quality": "sentence-transformers/multi-qa-mpnet-base-dot-v1",
}

DEFAULT_MODEL = "sentence-transformers/all-mpnet-base-v2"  # 768d


def _select_device():
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class EmbeddingService:
    def __init__(self, model_name: str = DEFAULT_MODEL, normalize=False, batch_size=32):
        self.device = _select_device()
        self.model = SentenceTransformer(model_name, device=self.device)
        self.normalize = normalize
        self.batch_size = batch_size

        print(f"[EMBEDDER] Model: {model_name}")
        print(f"[EMBEDDER] Device: {self.device}\n")

    def embed(self, texts: List[str], batch_size: int = None) -> List[List[float]]:
        batch_size = batch_size or self.batch_size
        vectors = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize,
        )
        return vectors.tolist()

    def embed_single(self, text: str) -> List[float]:
        return self.embed([text])[0]


hf_embedder = EmbeddingService()
