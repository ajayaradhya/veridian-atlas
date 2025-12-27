"""
embedder.py
-----------
Local Hugging Face embedding service for Veridian Atlas.

Key Improvements:
- Automatic GPU / CPU / MPS detection
- Batch size argument for throughput control
- Unified dtype + consistent return shapes
- Safe normalization toggle (optional)
- Model registry to future-proof upgrades
"""

from typing import List, Union
import torch
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------
# MODEL OPTIONS (swap here to upgrade quality)
# ---------------------------------------------------------
EMBEDDING_MODELS = {
    "fast": "sentence-transformers/all-MiniLM-L6-v2",       # quick, lightweight
    "balanced": "sentence-transformers/all-mpnet-base-v2",  # better accuracy
    "high_quality": "sentence-transformers/multi-qa-mpnet-base-dot-v1"
}

DEFAULT_MODEL = EMBEDDING_MODELS["fast"]


# ---------------------------------------------------------
# DEVICE SELECTION
# ---------------------------------------------------------
def _select_device():
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():     # Apple Silicon (M1/M2/M3)
        return "mps"
    return "cpu"


# ---------------------------------------------------------
# EMBEDDING SERVICE
# ---------------------------------------------------------
class EmbeddingService:
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        normalize: bool = False,
        batch_size: int = 32
    ):
        self.device = _select_device()
        self.model = SentenceTransformer(model_name, device=self.device)
        self.normalize = normalize
        self.batch_size = batch_size

        print(f"[EMBEDDER] Loaded model: {model_name}")
        print(f"[EMBEDDER] Device: {self.device}  | Batch size: {batch_size}")

    # ------------------------------
    # Batch embedding
    # ------------------------------
    def embed(
        self,
        texts: List[str],
        batch_size: int = None
    ) -> List[List[float]]:
        batch_size = batch_size or self.batch_size
        vectors = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize
        )
        return vectors.tolist()

    # ------------------------------
    # Single text embedding
    # ------------------------------
    def embed_single(self, text: str) -> List[float]:
        vector = self.model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=self.normalize
        )[0]
        return vector.tolist()


# ---------------------------------------------------------
# DEFAULT INSTANCE
# ---------------------------------------------------------
hf_embedder = EmbeddingService()
