"""
index_builder.py
----------------
Builds and manages a Chroma vector index from Veridian Atlas chunks.

Input:
    chunks.jsonl (output from chunker.py)

Output:
    chroma_db/  (local persistent vector DB for retrieval)

Enhancements:
- Accepts "content", "text", or "section_text" as the primary payload
- Normalizes metadata → Chroma-safe dict
- Prevents orphan fields & duplicated inserts
- Optional auto-reset via parameter
- Upsert-like behavior: same ID = overwrite
"""

from pathlib import Path
import json
import shutil
import chromadb
from chromadb.config import Settings
from veridian_atlas.embeddings.embedder import hf_embedder  # HF local embedder


# ---------------------------------------------
# CONFIG
# ---------------------------------------------

COLLECTION_NAME = "veridian_atlas"


def get_chroma_client(db_path: Path):
    """Create or connect to local Chroma DB."""
    db_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )


def get_or_create_collection(client):
    """Load or create vector collection."""
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # better for sentence-transformers
    )


# ---------------------------------------------
# INDEX BUILDING
# ---------------------------------------------

def build_chroma_index(
    chunks_path: Path,
    db_path: Path,
    reset_existing: bool = False,
    batch_size: int = 64
):
    """
    Build or update a Chroma index with embeddings from chunks.jsonl.

    Args
    ----
    chunks_path     : Path to chunks.jsonl
    db_path         : Directory to store / load index
    reset_existing  : If True → wipe old index first
    batch_size      : Embedding batch size
    """

    if not chunks_path.exists():
        raise FileNotFoundError(f"[ERROR] chunks.jsonl missing → {chunks_path}")

    if reset_existing and db_path.exists():
        print(f"[RESET] Removing old Chroma index → {db_path}")
        shutil.rmtree(db_path)

    print(f"\n[LOAD] Reading chunks from → {chunks_path}")
    print(f"[DB] Target Chroma path → {db_path}\n")

    client = get_chroma_client(db_path)
    collection = get_or_create_collection(client)

    ids, contents, metadatas = [], [], []

    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            raw = json.loads(line)

            # unified reader for all variants of text fields
            content = raw.get("content") or raw.get("text") or raw.get("section_text")
            if not content or not content.strip():
                continue

            chunk_id = raw["chunk_id"]

            # build chroma-safe metadata (nested dicts removed)
            metadata = {
                "deal_name": raw.get("deal_name"),
                "source_file": raw.get("source_file"),
                "level": raw.get("level"),
                "section_id": raw.get("section_id"),
                "clause_id": raw.get("clause_id"),
                "section_title": raw.get("section_title"),
                "clause_title": raw.get("clause_title"),
            }

            ids.append(chunk_id)
            contents.append(content.strip())
            metadatas.append({k: v for k, v in metadata.items() if v is not None})

    print(f"[STATS] Found {len(ids)} chunks with content.")
    if len(ids) == 0:
        print("[WARN] No valid chunks to embed. Aborting.")
        return collection

    # -----------------------------------------
    # BATCH EMBEDDINGS + INSERT
    # -----------------------------------------
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i+batch_size]
        batch_texts = contents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]

        vectors = hf_embedder.embed(batch_texts)

        collection.upsert(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=batch_meta,
            embeddings=vectors
        )

        print(f"[BATCH] Stored chunks {i} → {i + len(batch_ids) - 1}")

    print(f"\n[OK] Indexed {len(ids)} chunks into → {db_path}")
    return collection


# ---------------------------------------------
# FORCE REBUILD
# ---------------------------------------------

def rebuild_index(chunks_path: Path, db_path: Path):
    if db_path.exists():
        print(f"[REBUILD] Clearing index folder → {db_path}")
        shutil.rmtree(db_path)
    return build_chroma_index(chunks_path, db_path, reset_existing=False)


# ---------------------------------------------
# TEST QUERY
# ---------------------------------------------

def test_query(db_path: Path, question: str, n: int = 3):
    client = get_chroma_client(db_path)
    collection = get_or_create_collection(client)

    results = collection.query(query_texts=[question], n_results=n)

    print("\n=========== QUERY TEST ===========")
    print("Q:", question)
    print("----------------------------------")

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    for i, (doc, meta) in enumerate(zip(docs, metas), start=1):
        print(f"#{i}")
        print("Source:", meta.get("source_file"))
        print("Section:", meta.get("section_id"), "| Clause:", meta.get("clause_id"))
        print("Text:", doc)
        print("----------------------------------")

    return results
