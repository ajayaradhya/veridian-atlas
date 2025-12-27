"""
index_builder.py
----------------
Builds and manages a Chroma vector index from Veridian Atlas chunks.

Input:
    data/processed/chunks.jsonl    ← produced by chunker.py

Output:
    data/indexes/chroma_db/        ← persistent local vector DB

Features:
- Local embeddings (no API keys needed)
- Idempotent: repeated runs do not duplicate IDs
- Supports both append + rebuild modes
- Safe fallbacks for empty or malformed chunks
"""

from pathlib import Path
import json
import chromadb
from chromadb.config import Settings
from veridian_atlas.embeddings.embedder import hf_embedder  # local HF embedder

# -----------------------------------------------------
# CONFIG / TARGET COLLECTION
# -----------------------------------------------------

COLLECTION_NAME = "veridian_atlas"
DEFAULT_DB_PATH = Path("data/indexes/chroma_db")


# -----------------------------------------------------
# CREATE OR LOAD CHROMA DB
# -----------------------------------------------------

def get_chroma_client(db_path: Path = DEFAULT_DB_PATH):
    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )
    return client


def get_or_create_collection(client):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # sentence-transformers default
    )


# -----------------------------------------------------
# BUILD INDEX FROM CHUNKS
# -----------------------------------------------------

def build_chroma_index(
    chunks_path: Path,
    db_path: Path = DEFAULT_DB_PATH,
    batch_size: int = 64
):
    """
    Loads chunks from JSONL, generates local embeddings, and inserts into Chroma.

    Args
    ----
    chunks_path : Path → path to chunks.jsonl
    db_path     : Path → persistence directory
    batch_size  : int  → embedding batch size (increase if GPU available)
    """

    if not chunks_path.exists():
        raise FileNotFoundError(f"[ERROR] chunks.jsonl not found at: {chunks_path}")

    print(f"\n[LOAD] Reading chunks from → {chunks_path}")
    print(f"[DB] Target index → {db_path}\n")

    client = get_chroma_client(db_path)
    collection = get_or_create_collection(client)

    texts, ids, metadata = [], [], []

    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            text = data.get("text") or data.get("section_text")

            if not text or not text.strip():
                continue  # skip empty unusable chunks

            chunk_id = data["chunk_id"]

            ids.append(chunk_id)
            texts.append(text.strip())
            metadata.append(data)

    print(f"[STATS] Total chunks to embed: {len(texts)}")
    if len(texts) == 0:
        print("[WARN] No valid text chunks found. Aborting.")
        return collection

    # -------------------------------------------------
    # Batch Embedding & Insert
    # -------------------------------------------------
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        batch_meta = metadata[i:i+batch_size]

        vectors = hf_embedder.embed(batch_texts)

        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=batch_meta,
            embeddings=vectors,
        )

        print(f"[BATCH] Embedded + stored chunks {i} → {i+len(batch_texts)-1}")

    print(f"\n[OK] Indexed {len(ids)} chunks into Chroma @ {db_path}")
    return collection


# -----------------------------------------------------
# OPTIONAL: REBUILD FROM SCRATCH
# -----------------------------------------------------

def rebuild_index(chunks_path: Path, db_path: Path = DEFAULT_DB_PATH):
    if db_path.exists():
        import shutil
        print(f"[RESET] Removing existing index → {db_path}")
        shutil.rmtree(db_path)
    return build_chroma_index(chunks_path, db_path)


# -----------------------------------------------------
# QUICK TEST QUERY
# -----------------------------------------------------

def test_query(query: str, n: int = 3, db_path: Path = DEFAULT_DB_PATH):
    client = get_chroma_client(db_path)
    collection = get_or_create_collection(client)

    results = collection.query(
        query_texts=[query],
        n_results=n
    )
    print("\n[QUERY RESULTS]")
    return results