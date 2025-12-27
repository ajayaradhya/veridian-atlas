# veridian_atlas/kickoff/start_embeddings.py
"""
Embedding kickoff script.
Builds per-deal vector collections:
    VA::{deal_name}
using a shared DB:
    veridian_atlas/data/indexes/chroma_db
"""

from pathlib import Path
import argparse
from chromadb import PersistentClient
from chromadb.config import Settings
from veridian_atlas.index.index_builder import build_chroma_index


def get_args():
    p = argparse.ArgumentParser(description="Generate embeddings per deal.")
    p.add_argument("--deal", type=str, help="Single deal to embed")
    p.add_argument("--reset", action="store_true", help="Reset DB before embedding")
    return p.parse_args()


def embed_single_deal(deal: str, reset: bool):
    chunks_path = Path(f"veridian_atlas/data/deals/{deal}/processed/chunks.jsonl")
    db_path = Path("veridian_atlas/data/indexes/chroma_db")

    if not chunks_path.exists():
        raise FileNotFoundError(f"[ERROR] chunks.jsonl missing → {chunks_path}")

    print(f"\n--------------------------------------------------")
    print(f"Embedding deal:  {deal}")
    print(f"Collection:      VA_{deal}")
    print(f"Chunks source:   {chunks_path}")
    print(f"DB (shared):     {db_path}")
    print("--------------------------------------------------\n")

    build_chroma_index(
        deal_name=deal,
        chunks_path=chunks_path,
        db_path=db_path,
        reset_existing=reset,
    )


def embed_all(reset: bool):
    base = Path("veridian_atlas/data/deals")
    reset_flag = reset

    for deal_dir in base.iterdir():
        if not deal_dir.is_dir():
            continue
        deal = deal_dir.name
        chunks_path = deal_dir / "processed" / "chunks.jsonl"
        if chunks_path.exists():
            embed_single_deal(deal, reset=reset_flag)
            reset_flag = False   # only reset DB on first pass if requested

    print("\n[COMPLETE] All deals embedded.\n")


if __name__ == "__main__":
    args = get_args()

    if args.deal:
        embed_single_deal(args.deal, reset=args.reset)
    else:
        embed_all(reset=args.reset)

    print("[READY] Vector DB prepared.")
