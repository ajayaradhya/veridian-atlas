# veridian_atlas/rag/query_service.py
from typing import Dict, Any
import torch
from veridian_atlas.rag_engine.pipeline.rag_engine import answer_query, get_chroma_collection

class QueryService:
    def __init__(self, db_path: str = "veridian_atlas/data/indexes/chroma_db"):
        self.db_path = db_path

    def answer(self, deal_id: str, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Corrected: route to specific deal instead of global index.
        """
        result = answer_query(query=query, deal_name=deal_id, top_k=top_k)

        return {
            "deal_id": deal_id,
            "query": query,
            "answer": result.get("answer"),
            "citations": result.get("citations"),
            "retrieved_chunks": result.get("retrieved_chunks", []),
            "sources": result.get("sources", [])
        }

    def health(self, deal_id: str | None = None) -> Dict[str, Any]:
        try:
            if deal_id:
                _ = get_chroma_collection(deal_id)
            db_status = True
        except Exception:
            db_status = False

        return {
            "database_connected": db_status,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "deal_check": deal_id or "not provided"
        }
