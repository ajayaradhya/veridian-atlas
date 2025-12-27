# veridian_atlas/kickoff/start_embeddings.py

from pathlib import Path
from chromadb import PersistentClient
from chromadb.config import Settings
from veridian_atlas.index.index_builder import build_chroma_index

TEST_QUERY = "What is the interest rate for the Revolving Credit Facility?"
COLLECTION_NAME = "veridian_atlas"  # must match index_builder.py

if __name__ == "__main__":
    deal = "Blackbay_III"
    chunks_path = Path(f"veridian_atlas/data/deals/{deal}/processed/chunks.jsonl")
    db_path = Path("veridian_atlas/data/indexes/chroma_db")

    print("--------------------------------------------------")
    print(f"Building embeddings for deal: {deal}")
    print(f"Chunks:     {chunks_path}")
    print(f"DB Target:  {db_path}")
    print("--------------------------------------------------")

    # Safety Checks
    if not chunks_path.exists():
        raise FileNotFoundError(f"[ERROR] chunks.jsonl missing → {chunks_path}")
    if chunks_path.stat().st_size == 0:
        raise RuntimeError("[ERROR] chunks.jsonl is empty. Run chunker.py first.")

    # --------------------------------------------------
    # STEP 1: Build / Refresh Chroma Index
    # --------------------------------------------------
    build_chroma_index(
        chunks_path=chunks_path,
        db_path=db_path,
        reset_existing=True
    )
    print("\n[OK] Embeddings + Chroma index build complete.\n")

    # --------------------------------------------------
    # STEP 2: Connect to DB for quick sanity check
    # --------------------------------------------------
    client = PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )

    collections = client.list_collections()
    print("[CHECK] Collections found:")
    for col in collections:
        print(" -", col.name)
    print("--------------------------------------------------")

    if COLLECTION_NAME not in [c.name for c in collections]:
        raise RuntimeError(f"[FAIL] Missing expected collection: {COLLECTION_NAME}")

    collection = client.get_collection(COLLECTION_NAME)

    # --------------------------------------------------
    # STEP 3: TEST QUERY
    # --------------------------------------------------
    print("[TEST QUERY]")
    print("Query:", TEST_QUERY, "\n")

    results = collection.query(
        query_texts=[TEST_QUERY],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    print("Top Matches:")
    for doc, meta, score in zip(docs, metas, dists):
        print("--------------------------------------------------")
        print(f"Score:      {score:.4f}")
        print(f"Chunk ID:   {meta.get('chunk_id')}")
        print(f"Section:    {meta.get('section_id')} | Clause: {meta.get('clause_id')}")
        print("Text:")
        print(doc[:280] + ("..." if len(doc) > 280 else ""))

    print("--------------------------------------------------")
    print("[OK] Embeddings & retrieval test completed successfully.")
