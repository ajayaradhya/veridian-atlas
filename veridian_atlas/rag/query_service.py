# veridian_atlas/rag/query_service.py
from typing import Dict, Any
import torch
from veridian_atlas.rag.rag_engine import answer_query, get_chroma_collection


class QueryService:
    def __init__(
        self,
        db_path: str = "veridian_atlas/data/indexes/chroma_db",
        model_name: str | None = None
    ):
        """
        Initializes the unified Query Service layer which
        sits between the API and the RAG engine.
        """
        self.db_path = db_path
        self.model_name = model_name


    # --------------------------------------------------
    # MAIN ENTRYPOINT FOR API / UI / REQUESTS
    # --------------------------------------------------
    def answer(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        High-level API-facing entrypoint.
        Uses the updated rag_engine.answer_query.
        Always returns UI-safe normalized structure.
        """
        result = answer_query(query, top_k)

        return {
            "query": result.get("query"),
            "answer": result.get("answer"),
            "citations": result.get("citations"),
            "citations_model": result.get("citations_model", []),
            "citations_retrieved": result.get("citations_retrieved", []),
            "source_count": len(result.get("sources", [])),
            "sources": result.get("sources", [])
        }


    # --------------------------------------------------
    # HEALTH & SYSTEM STATE FOR UI (Swagger / Dashboard)
    # --------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Returns system capability status for UI pre-checks:
        - DB reachable?
        - Model in memory?
        - GPU or CPU mode?
        """
        # Check Chroma and device state
        try:
            _ = get_chroma_collection(self.db_path)
            db_status = True
        except Exception:
            db_status = False

        gpu_available = torch.cuda.is_available()
        device = "cuda" if gpu_available else "cpu"

        return {
            "status": "ok" if db_status else "error",
            "database_connected": db_status,
            "device": device,
            "gpu": gpu_available,
            "model": self.model_name or "Qwen-0.5B (default)"
        }
