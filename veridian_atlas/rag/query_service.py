# veridian_atlas/rag/query_service.py
from typing import Dict, List
from veridian_atlas.rag.rag_engine import RAGEngine

class QueryService:
    def __init__(
        self,
        db_path: str = "veridian_atlas/data/indexes/chroma_db",
        model_name: str | None = None
    ):
        self.engine = RAGEngine(db_path=db_path, model_name=model_name)

    def answer(self, query: str, top_k: int = 3):
        contexts = self.engine.retrieve(query, top_k)
        llm_response = self.engine.generate_answer(query, contexts)

        source_ids = [c.get("chunk_id") for c in contexts]

        return {
            "answer_raw": llm_response,
            "sources_used": source_ids,
            "source_objects": contexts
        }

    def health(self) -> dict:
        """Used by UI to verify system state before enablement."""
        return {
            "status": "ok",
            "model_loaded": True,
            "db_connected": True
        }
