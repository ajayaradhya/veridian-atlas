"""
rag_engine.py
-------------
Core RAG workflow with corrected JSON handling and citation separation.
"""

from pathlib import Path
from typing import List, Dict, Any
import json, chromadb
from chromadb.config import Settings

from veridian_atlas.rag.local_llm import generate_response

DEFAULT_DB_PATH = Path("veridian_atlas/data/indexes/chroma_db")
COLLECTION_NAME = "veridian_atlas"
TOP_K = 5


def get_chroma_collection(db_path: Path = DEFAULT_DB_PATH):
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception as err:
        raise RuntimeError(
            f"[RAG ERROR] No Chroma collection named '{COLLECTION_NAME}'. "
            "Run embedding setup: python -m veridian_atlas.kickoff.start_embeddings"
        ) from err


def retrieve_context(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    collection = get_chroma_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    contexts = []
    for doc, meta, dist in zip(docs, metas, dists):
        contexts.append({
            "chunk_id": meta.get("chunk_id", "UNKNOWN_CHUNK"),
            "content": doc.replace("\n", " ").strip(),
            "section": meta.get("section_id"),
            "clause": meta.get("clause_id"),
            "distance": float(dist),
        })
    return contexts


def build_rag_prompt(query: str, contexts: List[dict]) -> str:
    blocks = [f"[{c['chunk_id']}] {c['content']}" for c in contexts]
    context_text = "\n".join(blocks)

    return f"""
You are a financial contract analysis assistant.

Use ONLY the context provided. If the answer is not present, respond exactly:
"The provided text does not contain enough information."

QUESTION:
{query}

CONTEXT:
{context_text}

RESPONSE RULES:
- Respond ONLY in valid JSON.
- "answer" must be short and factual.
- "citations" must reference chunk IDs exactly as shown.

OUTPUT FORMAT:
{{
  "answer": "...",
  "citations": ["chunk_id"]
}}
""".strip()


def answer_query(query: str, top_k: int = TOP_K) -> Dict[str, Any]:
    contexts = retrieve_context(query, top_k)

    if not contexts:
        return {
            "query": query,
            "answer": "The provided text does not contain enough information.",
            "citations_model": [],
            "citations_retrieved": [],
            "sources": []
        }

    prompt = build_rag_prompt(query, contexts)
    model_json = generate_response(prompt)

    return {
        "query": query,
        "answer": model_json.get("answer"),
        "citations": model_json.get("citations", []),
        "citations_model": model_json.get("citations", []),        # from model
        "citations_retrieved": [c["chunk_id"] for c in contexts],  # from vector DB
        "sources": contexts
    }


if __name__ == "__main__":
    test_question = "What is the interest rate for the Revolving Credit Facility?"
    print(answer_query(test_question))
