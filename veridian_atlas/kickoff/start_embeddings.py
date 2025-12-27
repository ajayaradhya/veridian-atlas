# veridian_atlas/kickoff/start_embeddings.py
"""
Embedding kickoff script (per-deal collections)

Collections created:
    VA_{deal_name}

DB Root:
    veridian_atlas/data/indexes/chroma_db

Usage:
    python -m veridian_atlas.kickoff.start_embeddings --reset
    python -m veridian_atlas.kickoff.start_embeddings --deal Blackbay_III
"""

from pathlib import Path
import argparse
from veridian_atlas.index.index_builder import build_chroma_index


# -----------------------------------------------------
# CLI ARGUMENTS
# -----------------------------------------------------

def get_args():
    parser = argparse.ArgumentParser(description="Generate embeddings per deal.")
    parser.add_argument("--deal", type=str, help="Single deal to embed (e.g. Blackbay_III)")
    parser.add_argument("--reset", action="store_true", help="Reset DB before embedding (only once)")
    return parser.parse_args()


# -----------------------------------------------------
# SINGLE DEAL EMBEDDING
# -----------------------------------------------------

def embed_single_deal(deal: str, reset: bool):
    chunks_path = Path(f"veridian_atlas/data/deals/{deal}/processed/chunks.jsonl")
    db_path = Path("veridian_atlas/data/indexes/chroma_db")

    if not chunks_path.exists():
        raise FileNotFoundError(f"[ERROR] Missing chunks.jsonl → {chunks_path}\nRun chunker first.")

    print("\n--------------------------------------------------")
    print(f"[EMBED] DEAL:        {deal}")
    print(f"[COLLECTION NAME]:   VA_{deal}")
    print(f"[CHUNKS SOURCE]:     {chunks_path}")
    print(f"[DB PATH]:           {db_path}")
    print(f"[RESET]:             {'YES' if reset else 'NO'}")
    print("--------------------------------------------------\n")

    build_chroma_index(
        deal_name=deal,
        chunks_path=chunks_path,
        db_path=db_path,
        reset_existing=reset,
    )


# -----------------------------------------------------
# MULTI-DEAL BATCH MODE
# -----------------------------------------------------

def embed_all(reset: bool):
    base = Path("veridian_atlas/data/deals")

    # Only reset once at the start, not for every deal
    reset_first = reset

    for deal_dir in base.iterdir():
        if not deal_dir.is_dir():
            continue

        deal = deal_dir.name
        chunks_path = deal_dir / "processed" / "chunks.jsonl"

        if chunks_path.exists():
            embed_single_deal(deal, reset=reset_first)
            reset_first = False  # Prevent wiping DB for subsequent deals
        else:
            print(f"[SKIP] No chunks.jsonl for: {deal}")

    print("\n==================================================")
    print("[COMPLETE] All deals embedded successfully.")
    print("==================================================\n")


# -----------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------

if __name__ == "__main__":
    args = get_args()

    if args.deal:
        embed_single_deal(args.deal, reset=args.reset)
    else:
        embed_all(reset=args.reset)

    print("[READY] Vector DB prepared and ready for RAG.\n")
