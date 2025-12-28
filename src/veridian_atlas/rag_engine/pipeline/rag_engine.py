"""
rag_engine.py
-------------
Per-deal RAG engine (improved):
 - Per-deal collections → VA_{deal_name}
 - Manual embedding for queries (no dimension mismatch)
 - Allows semantic paraphrasing (no overstrict substring match)
 - Still prevents hallucinated citations
"""

from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings

from veridian_atlas.rag_engine.services.local_llm import generate_response
from veridian_atlas.data_pipeline.processors.embedder import hf_embedder

DEFAULT_DB_PATH = Path("veridian_atlas/data/indexes/chroma_db")
TOP_K = 5


# ------------------------------------------------------------
# COLLECTION ACCESS (one per deal)
# ------------------------------------------------------------
def get_chroma_collection(deal_name: str, db_path: Path = DEFAULT_DB_PATH):
    collection_name = f"VA_{deal_name}".replace(" ", "_")
    client = chromadb.PersistentClient(
        path=str(db_path), settings=Settings(anonymized_telemetry=False)
    )
    return client.get_collection(collection_name)


# ------------------------------------------------------------
# RETRIEVAL (manual embedding fixes 384 vs 768 errors)
# ------------------------------------------------------------
def retrieve_context(query: str, deal_name: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    collection = get_chroma_collection(deal_name)
    if collection is None:
        return []
    # Manual embedding → avoids auto-embed mismatch
    q_vec = hf_embedder.embed_single(query)

    results = collection.query(
        query_embeddings=[q_vec],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    return [
        {
            "chunk_id": m.get("chunk_id"),
            "content": d.replace("\n", " ").strip(),
            "section": m.get("section_id"),
            "clause": m.get("clause_id"),
            "distance": float(dist),
        }
        for d, m, dist in zip(docs, metas, dists)
    ]


# ------------------------------------------------------------
# PROMPT BUILDER (restores original behavior)
# ------------------------------------------------------------
def build_rag_prompt(query: str, contexts: List[dict], deal_name: str) -> str:
    ctx = "\n".join([f"[{c['chunk_id']}] {c['content']}" for c in contexts])

    return f"""
You are a financial contract assistant. Use ONLY the provided context.

RULES:
- If the answer is not present, respond exactly:
  "The provided text does not contain enough information."
- Respond in pure JSON. No explanations. No bullets. No prose.
- Citations must reference chunk_ids exactly as shown.

QUESTION:
{query}

CONTEXT:
{ctx}

RESPONSE FORMAT (JSON ONLY):
{{
  "answer": "short answer here",
  "citations": ["chunk_id_1", "chunk_id_2"]
}}
""".strip()


# ------------------------------------------------------------
# MAIN ENTRYPOINT
# ------------------------------------------------------------
def answer_query(query: str, deal_name: str, top_k: int = TOP_K) -> Dict[str, Any]:
    contexts = retrieve_context(query, deal_name, top_k)

    if not contexts:
        return {
            "query": query,
            "deal": deal_name,
            "answer": "The provided text does not contain enough information.",
            "citations": [],
            "retrieved_chunks": [],
            "sources": [],
        }

    prompt = build_rag_prompt(query, contexts, deal_name)
    raw = generate_response(prompt)

    model_answer = raw.get("answer", "").strip()
    model_citations = raw.get("citations", [])

    # Valid retrieved chunk IDs
    retrieved_ids = [c["chunk_id"] for c in contexts]

    # Step 1 — Keep only citations that actually exist in retrieval
    citations = [c for c in model_citations if c in retrieved_ids]

    # Step 2 — Only reject if citations reference chunks that do not exist
    if any(c not in retrieved_ids for c in model_citations):
        model_answer = "The provided text does not contain enough information."
        citations = []

    # Step 3 — Allow paraphrasing; we do NOT require substring match anymore
    if not citations and model_answer != "The provided text does not contain enough information.":
        # No valid evidence; cannot justify answer
        model_answer = "The provided text does not contain enough information."

    return {
        "query": query,
        "deal": deal_name,
        "answer": model_answer,
        "citations": citations,
        "retrieved_chunks": retrieved_ids,
        "sources": contexts,
    }
