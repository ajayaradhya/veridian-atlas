# veridian_atlas/kickoff/start_embeddings.py
"""
Kickstart: Build or update embeddings + Chroma index from chunks.jsonl,
then run a retrieval test to confirm index behavior.

Run AFTER:
- text_loader/router
- chunker.py

Command:
    python -m veridian_atlas.kickoff.start_embeddings
"""

from pathlib import Path
from chromadb import PersistentClient
from chromadb.config import Settings
from veridian_atlas.index.index_builder import build_chroma_index

TEST_QUERY = "What is the interest rate for the Revolving Credit Facility?"

# This MUST match index_builder.py
COLLECTION_NAME = "veridian_atlas"

if __name__ == "__main__":
    deal = "Blackbay_III"
    chunks_path = Path(f"veridian_atlas/data/deals/{deal}/processed/chunks.jsonl")
    db_path = Path("veridian_atlas/data/indexes/chroma_db")

    print("--------------------------------------------------")
    print(f"Building embeddings for deal: {deal}")
    print(f"Chunks:     {chunks_path}")
    print(f"DB Target:  {db_path}")
    print("--------------------------------------------------")

    # PRECHECK
    if not chunks_path.exists():
        raise FileNotFoundError(f"[ERROR] chunks.jsonl missing → {chunks_path}")
    if chunks_path.stat().st_size == 0:
        raise RuntimeError("[ERROR] chunks.jsonl is empty. Run chunker.py first.")

    # STEP 1: Build / Refresh Index
    build_chroma_index(chunks_path, db_path, reset_existing=True)
    print("[OK] Embeddings + Chroma index build complete.\n")

    # STEP 2: Connect to DB
    client = PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )

    # STEP 3: Validate Collections
    collections = client.list_collections()
    print("[CHECK] Collections found:")
    for col in collections:
        print(" -", col.name)
    print("--------------------------------------------------")

    if COLLECTION_NAME not in [c.name for c in collections]:
        raise RuntimeError(
            f"[FAIL] Expected collection '{COLLECTION_NAME}' not found. "
            "Index may not have built correctly."
        )

    # Get the correct collection
    collection = client.get_collection(name=COLLECTION_NAME)

    # STEP 4: Test Query
    print("[TEST QUERY]")
    print("Query:", TEST_QUERY, "\n")

    results = collection.query(
        query_texts=[TEST_QUERY],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    docs = results.get("documents", [[]])[0]
    meta = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    print("Top Matches:")
    for doc, m, score in zip(docs, meta, dists):
        print("--------------------------------------------------")
        print(f"Score:    {score:.4f}")
        print(f"Section:  {m.get('section_id')}")
        print(f"Clause:   {m.get('clause_id')}")
        print("Text:")
        print(doc[:300] + ("..." if len(doc) > 300 else ""))

    print("--------------------------------------------------")
    print("[OK] Embeddings & retrieval test completed successfully.")
