"""
index_builder.py
----------------
Final version:
 - One collection per deal → VA_{deal_name}
 - No server-side embedding functions
 - All embeddings done manually with hf_embedder
 - Dimension mismatches prevented
"""

from pathlib import Path
import json
import chromadb
from chromadb.config import Settings
from veridian_atlas.data_pipeline.processors.embedder import hf_embedder


def get_chroma_client(db_path: Path):
    db_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )


def get_or_create_deal_collection(client, deal_name: str):
    collection_name = f"VA_{deal_name}".replace(" ", "_")
    current_dim = len(hf_embedder.embed_single("DIM_CHECK"))

    try:
        col = client.get_collection(collection_name)
        stored_dim = col.get()["metadata"].get("model_dim")

        if stored_dim and stored_dim != current_dim:
            print(f"[DIMENSION MISMATCH] {collection_name}: {stored_dim} != {current_dim}")
            print("[ACTION] Dropping old collection...")
            client.delete_collection(collection_name)
            raise Exception("recreate")

        return col

    except Exception:
        # IMPORTANT: no embedding_function here
        return client.get_or_create_collection(
            name=collection_name,
            metadata={"model_dim": current_dim, "model_name": "mpnet-base-v2"},
        )


def build_chroma_index(
    deal_name: str,
    chunks_path: Path,
    db_path: Path,
    reset_existing: bool = False,
    batch_size: int = 64
):
    if not chunks_path.exists():
        raise FileNotFoundError(f"[ERROR] chunks.jsonl missing → {chunks_path}")

    client = get_chroma_client(db_path)
    collection_name = f"VA_{deal_name}".replace(" ", "_")

    if reset_existing:
        try:
            client.delete_collection(collection_name)
            print(f"[RESET] Cleared old → {collection_name}")
        except Exception:
            pass

    collection = get_or_create_deal_collection(client, deal_name)

    ids, docs, metas = [], [], []

    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            content = data.get("content", "").strip()
            if not content:
                continue

            ids.append(data["chunk_id"])
            docs.append(content)
            metas.append({
                "chunk_id": data["chunk_id"],
                "deal_name": data.get("deal_name"),
                "document_id": data.get("document_id"),
                "document_display_name": data.get("document_display_name"),
                "section_id": data.get("section_id"),
                "normalized_section": data.get("normalized_section"),
                "clause_id": data.get("clause_id"),
                "source_path": data["metadata"].get("source_path"),
            })

    print(f"[STATS] {len(ids)} chunks detected. Embedding now...")

    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i+batch_size]
        batch_docs = docs[i:i+batch_size]
        batch_meta = metas[i:i+batch_size]

        vectors = hf_embedder.embed(batch_docs)

        collection.upsert(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_meta,
            embeddings=vectors
        )
        print(f"[BATCH] {i} → {i+len(batch_ids)-1}")

    print(f"[OK] Completed → {collection_name}")
    return collection
