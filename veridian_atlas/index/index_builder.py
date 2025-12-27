"""
index_builder.py
----------------
Build & maintain Chroma vector index for Veridian Atlas.
"""

from pathlib import Path
import json
import shutil
import chromadb
from chromadb.config import Settings
from veridian_atlas.embeddings.embedder import hf_embedder


COLLECTION_NAME = "veridian_atlas"


# -----------------------------------------------------
# DB CLIENT + COLLECTION
# -----------------------------------------------------

def get_chroma_client(db_path: Path):
    db_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_collection(client):
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # best for sentence-transformers
    )


# -----------------------------------------------------
# BUILD INDEX
# -----------------------------------------------------

def build_chroma_index(
    chunks_path: Path,
    db_path: Path,
    reset_existing: bool = False,
    batch_size: int = 64
):
    if not chunks_path.exists():
        raise FileNotFoundError(f"[ERROR] chunks.jsonl missing → {chunks_path}")

    # optional wipe
    if reset_existing and db_path.exists():
        print(f"[RESET] Removing old Chroma index → {db_path}")
        shutil.rmtree(db_path)

    print(f"\n[LOAD] Chunks → {chunks_path}")
    print(f"[DB]   Index  → {db_path}\n")

    client = get_chroma_client(db_path)
    collection = get_or_create_collection(client)

    ids, contents, metadatas = [], [], []

    # -------------------------------------------------
    # LOAD & NORMALIZE CHUNKS
    # -------------------------------------------------
    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)

            content = data.get("content") or data.get("text") or data.get("section_text")
            if not content or not content.strip():
                continue

            chunk_id = data["chunk_id"]

            ### FIX: force ID into metadata now
            metadata = {
                "chunk_id": chunk_id,                        # <— KEY LINE
                "deal_name": data.get("deal_name"),
                "source_file": data.get("source_file"),
                "level": data.get("level"),
                "section_id": data.get("section_id"),
                "clause_id": data.get("clause_id"),
                "section_title": data.get("section_title"),
                "clause_title": data.get("clause_title"),
            }

            ids.append(chunk_id)
            contents.append(content.strip())
            metadatas.append({k: v for k, v in metadata.items() if v is not None})

    print(f"[STATS] {len(ids)} valid chunks to index.")
    if len(ids) == 0:
        print("[WARN] No usable chunks found. Exiting.")
        return collection

    # -------------------------------------------------
    # EMBED + UPSERT
    # -------------------------------------------------
    for i in range(0, len(ids), batch_size):
        b_ids = ids[i:i+batch_size]
        b_text = contents[i:i+batch_size]
        b_meta = metadatas[i:i+batch_size]

        vectors = hf_embedder.embed(b_text)

        collection.upsert(                      # <— safe overwrite
            ids=b_ids,
            documents=b_text,
            metadatas=b_meta,
            embeddings=vectors,
        )

        print(f"[BATCH] {i} → {i + len(b_ids) - 1}")

    print(f"\n[OK] Indexed {len(ids)} chunks → {db_path}")
    return collection


# -----------------------------------------------------
# REBUILD
# -----------------------------------------------------

def rebuild_index(chunks_path: Path, db_path: Path):
    if db_path.exists():
        shutil.rmtree(db_path)
    return build_chroma_index(chunks_path, db_path, reset_existing=False)


# -----------------------------------------------------
# TEST QUERY
# -----------------------------------------------------

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
        print(f"#{i} | {meta.get('chunk_id')}")
        print(f"Section: {meta.get('section_id')} | Clause: {meta.get('clause_id')}")
        print(doc[:200], "...")
        print("----------------------------------")

    return results
