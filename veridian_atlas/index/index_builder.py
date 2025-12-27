"""
index_builder.py
----------------
Chroma index builder with per-deal collections.
Option B model:
    Single DB path
    One collection per deal → "VA::{deal_name}"
"""

from pathlib import Path
import json
import shutil
import chromadb
from chromadb.config import Settings
from veridian_atlas.embeddings.embedder import hf_embedder


# -----------------------------------------------------
# DB CLIENT (shared DB for all deals)
# -----------------------------------------------------

def get_chroma_client(db_path: Path):
    db_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )


# -----------------------------------------------------
# PER-DEAL COLLECTION
# -----------------------------------------------------

def get_or_create_deal_collection(client, deal_name: str):
    # Sanitized per Chroma naming rules
    collection_name = f"VA_{deal_name}".replace(" ", "_")
    
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


# -----------------------------------------------------
# BUILD INDEX (PER DEAL)
# -----------------------------------------------------

def build_chroma_index(
    deal_name: str,
    chunks_path: Path,
    db_path: Path,
    reset_existing: bool = False,
    batch_size: int = 64
):
    if not chunks_path.exists():
        raise FileNotFoundError(f"[ERROR] chunks.jsonl missing → {chunks_path}")

    # Optional reset → only affects this deal's collection
    if reset_existing and db_path.exists():
        print(f"[RESET] Removing DB path for rebuild → {db_path}")
        shutil.rmtree(db_path)

    print(f"\n[LOAD] Chunks: {chunks_path}")
    print(f"[DB]   Path : {db_path}")
    print(f"[COL]  Name : VA::{deal_name}\n")

    client = get_chroma_client(db_path)
    collection = get_or_create_deal_collection(client, deal_name)

    ids, texts, metadatas = [], [], []

    # -----------------------------------------------------
    # LOAD CHUNKS
    # -----------------------------------------------------
    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            content = data.get("content", "").strip()

            if not content:
                continue

            # Build metadata payload supported by our schema
            metadata = {
                "chunk_id": data["chunk_id"],
                "deal_name": data.get("deal_name"),
                "document_id": data.get("document_id"),
                "document_display_name": data.get("document_display_name"),
                "level": data.get("level"),
                "section_id": data.get("section_id"),
                "normalized_section": data.get("normalized_section"),
                "clause_id": data.get("clause_id"),
                "source_path": data["metadata"].get("source_path"),
                "file_hash": data["metadata"].get("file_hash"),
            }

            ids.append(data["chunk_id"])
            texts.append(content)
            metadatas.append(metadata)

    print(f"[STATS] {len(ids)} chunks detected.")

    if not ids:
        print("[WARN] No chunks found. Exiting.")
        return collection

    # -----------------------------------------------------
    # BATCHED EMBEDDING + UPSERT
    # -----------------------------------------------------
    for i in range(0, len(ids), batch_size):
        b_ids = ids[i:i + batch_size]
        b_txt = texts[i:i + batch_size]
        b_meta = metadatas[i:i + batch_size]

        vectors = hf_embedder.embed(b_txt)

        collection.upsert(
            ids=b_ids,
            documents=b_txt,
            metadatas=b_meta,
            embeddings=vectors,
        )

        print(f"[BATCH] Indexed {i} → {i + len(b_ids) - 1}")

    print(f"\n[OK] Completed embedding for deal → {deal_name}")
    print(f"[INDEX] Stored under collection → VA::{deal_name}\n")
    return collection
