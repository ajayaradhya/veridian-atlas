# veridian_atlas/kickstart_embeddings.py
"""
Kickstart: Build or update embeddings + Chroma index from chunks.jsonl
Then run a retrieval test to confirm everything is working.
"""

from pathlib import Path
from chromadb import PersistentClient
from veridian_atlas.index.index_builder import build_chroma_index

# Optional: change based on your HF model choice
TEST_QUERY = "What is the interest rate for the Revolving Credit Facility?"

if __name__ == "__main__":
    deal = "Blackbay_III"
    chunks_path = Path(f"veridian_atlas/data/deals/{deal}/processed/chunks.jsonl")
    db_path = Path("veridian_atlas/data/indexes/chroma_db")

    print("--------------------------------------------------")
    print(f"  Building embeddings for deal: {deal}")
    print(f"  Chunks: {chunks_path}")
    print(f"  DB Path: {db_path}")
    print("--------------------------------------------------")

    # STEP 1: Build / refresh embeddings
    build_chroma_index(chunks_path, db_path)
    print("[OK] Embeddings + Chroma index build complete.")

    # STEP 2: Load DB and check stored collections
    client = PersistentClient(path=str(db_path))
    collections = client.list_collections()

    print("\n[CHECK] Collections found:")
    for c in collections:
        print(f" - {c.name}")
    print(f"Total collections: {len(collections)}")

    # Expect one collection per deal (e.g., Blackbay_III)
    if not collections:
        raise RuntimeError("ERROR: No collections found. Did the indexing fail?")

    # STEP 3: Run a test query
    test_collection = client.get_collection(name=deal)
    print("\n[TEST QUERY]")
    print(f"Query: {TEST_QUERY}\n")

    results = test_collection.query(
        query_texts=[TEST_QUERY],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    # STEP 4: Print results
    print("Top Matches:")
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        print("--------------------------------------------------")
        print(f"Score:       {dist:.4f}")
        print(f"Section:     {meta.get('section_id')}")
        print(f"Clause:      {meta.get('clause_id')}")
        print("Text:")
        print(doc[:300] + ("..." if len(doc) > 300 else ""))
    print("--------------------------------------------------")

    print("\n[OK] Embeddings & retrieval test completed successfully.")
