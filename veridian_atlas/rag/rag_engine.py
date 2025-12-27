"""
rag_engine.py
-------------
Core Retrieval-Augmented Generation engine for Veridian Atlas.

Responsibilities:
- Connect to Chroma DB
- Retrieve relevant chunks for a query
- Build a citation-ready prompt
- Call a local LLM (Qwen) for final answer generation

Dependencies:
    pip install chromadb sentence-transformers
"""

from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings

from veridian_atlas.rag.local_llm import LocalQwenLLM  # Qwen model wrapper

# ----------------------------------------
# CONFIG
# ----------------------------------------

DEFAULT_DB_PATH = Path("veridian_atlas/data/indexes/chroma_db")
COLLECTION_NAME = "veridian_atlas"
TOP_K = 5  # number of chunks to retrieve per query


# ----------------------------------------
# Chroma Setup
# ----------------------------------------

def get_chroma_collection(db_path: Path = DEFAULT_DB_PATH):
    """Load Chroma client + target collection."""
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except:
        raise RuntimeError(
            f"[RAG] No Chroma collection named '{COLLECTION_NAME}' found. "
            f"Run embeddings/index builder first."
        )
    return collection


# ----------------------------------------
# Retrieval Layer
# ----------------------------------------

def retrieve_context(query: str, top_k: int = TOP_K) -> Dict[str, Any]:
    """
    Performs a similarity search and returns:
      - top documents
      - metadata for citation
      - reference mapping for prompt assembly
    """
    collection = get_chroma_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Flatten for easier consumption
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    # Build citation objects
    citations = []
    for doc, meta, dist in zip(docs, metas, dists):
        citations.append({
            "chunk_id": meta.get("chunk_id", "UNKNOWN"),
            "section": meta.get("section_id"),
            "clause": meta.get("clause_id"),
            "distance": float(dist),
            "content": doc
        })

    return {
        "docs": docs,
        "citations": citations,
        "context_blocks": docs,
    }


# ----------------------------------------
# Prompt Construction
# ----------------------------------------

def build_rag_prompt(query: str, context_blocks: List[str]) -> str:
    """
    Create a structured prompt for the Qwen model.
    """
    context_text = "\n\n--- SOURCE CHUNK ---\n\n".join(context_blocks)

    prompt = f"""
You are a financial contract assistant. Use ONLY the context below to answer.
If the answer is not present in the context, say "The provided text does not contain enough information."

QUESTION:
{query}

CONTEXT:
{context_text}

RULES:
- Answer concisely.
- Quote exact phrases when possible.
- Provide citations as a list of chunk IDs used.

FINAL ANSWER FORMAT (JSON):
{{
  "answer": "...the answer...",
  "citations": ["chunk_id_1", "chunk_id_2"]
}}
"""
    return prompt.strip()


# ----------------------------------------
# Generate Final Response
# ----------------------------------------

def answer_query(query: str) -> Dict[str, Any]:
    """
    Main RAG pipeline:
        retrieve → build prompt → generate answer → return structured result
    """
    retrieved = retrieve_context(query)
    context_blocks = retrieved["context_blocks"]

    if not context_blocks:
        return {
            "answer": "No relevant information found in the indexed documents.",
            "citations": []
        }

    # Build prompt for LLM
    prompt = build_rag_prompt(query, context_blocks)

    # Call local Qwen model
    llm = LocalQwenLLM()  # uses CPU
    llm_response = llm.generate(prompt)

    # Return combined structure
    return {
        "answer": llm_response,
        "citations": [c["chunk_id"] for c in retrieved["citations"]],
        "sources": retrieved["citations"]
    }


# ----------------------------------------
# If manually run
# ----------------------------------------

if __name__ == "__main__":
    test_q = "What is the interest rate for the Revolving Credit Facility?"
    result = answer_query(test_q)
    print("\n[RESULT]")
    print(result)
