"""
rag_engine.py
-------------
Core Retrieval-Augmented Generation engine for Veridian Atlas.

Responsibilities:
- Connect to Chroma and retrieve relevant chunks
- Build context-aware prompt with chunk IDs for citation
- Forward prompt to local Qwen-0.5B for JSON answer
- Return UI/Backend friendly structure
"""

from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings

from veridian_atlas.rag.local_llm import generate_response


# ----------------------------------------
# CONFIG
# ----------------------------------------

DEFAULT_DB_PATH = Path("veridian_atlas/data/indexes/chroma_db")
COLLECTION_NAME = "veridian_atlas"
TOP_K = 5


# ----------------------------------------
# CHROMA CONNECTION
# ----------------------------------------

def get_chroma_collection(db_path: Path = DEFAULT_DB_PATH):
    """
    Connect to Chroma and load the target collection.
    Raises a clear error if the index doesn't exist.
    """
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )

    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception as err:
        raise RuntimeError(
            f"[RAG ERROR] No Chroma collection named '{COLLECTION_NAME}'.\n"
            f"Run embeddings first → start_embeddings.py"
        ) from err


# ----------------------------------------
# RETRIEVAL LAYER
# ----------------------------------------

def retrieve_context(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """
    Run similarity search over vector DB.
    Always returns a list of context objects:
        { chunk_id, content, section, clause, distance }
    """
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
        chunk_id = (
            meta.get("chunk_id")
            or meta.get("id")
            or meta.get("section_id")
            or "UNKNOWN_CHUNK"
        )

        contexts.append({
            "chunk_id": chunk_id,
            "content": doc,
            "section": meta.get("section_id"),
            "clause": meta.get("clause_id"),
            "distance": float(dist),
        })

    return contexts


# ----------------------------------------
# PROMPT CONSTRUCTION
# ----------------------------------------

def build_rag_prompt(query: str, contexts: List[dict]) -> str:
    blocks = []
    for c in contexts:
        clean_text = c["content"].replace("\n", " ").strip()
        blocks.append(f"[{c['chunk_id']}] {clean_text}")

    context_text = "\n".join(blocks)

    prompt = f"""
You are a financial contract analysis assistant.

Use ONLY the context provided. If the answer is not present, respond exactly with:
"The provided text does not contain enough information."

QUESTION:
{query}

CONTEXT:
{context_text}

RESPONSE RULES:
- Respond ONLY in valid JSON.
- "answer" must be a short sentence.
- "citations" must reference only chunk IDs from the context.
- No prose, no markdown, no extra text — JSON only.

OUTPUT FORMAT:
{{
  "answer": "...",
  "citations": ["chunk_id_1", "chunk_id_2"]
}}
""".strip()

    return prompt



# ----------------------------------------
# MAIN QUERY PIPELINE
# ----------------------------------------

def answer_query(query: str, top_k: int = TOP_K) -> Dict[str, Any]:
    """
    Full RAG pipeline:
        1. retrieve context chunks
        2. build prompt
        3. pass to model
        4. return citation-linked JSON
    """
    contexts = retrieve_context(query, top_k=top_k)

    # no retrieval results
    if not contexts:
        return {
            "query": query,
            "answer": "The provided text does not contain enough information.",
            "citations": [],
            "sources": []
        }

    prompt = build_rag_prompt(query, contexts)
    llm_response = generate_response(prompt)

    # final payload for UI or API response
    return {
        "query": query,
        "answer": llm_response,
        "citations": [c["chunk_id"] for c in contexts],
        "sources": contexts
    }


# ----------------------------------------
# Manual Test
# ----------------------------------------

if __name__ == "__main__":
    test_question = "What is the interest rate for the Revolving Credit Facility?"
    result = answer_query(test_question)
    print(result)
