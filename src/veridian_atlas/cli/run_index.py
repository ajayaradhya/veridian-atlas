"""
run_index.py
-----------------
Build or rebuild ChromaDB vector indexes for one or all deals.

Note:
    This step already handles embeddings internally as part of
    build_chroma_index(), so no separate embedding step is required.

CLI Usage:
    python -m veridian_atlas.cli.run_index --reset
    python -m veridian_atlas.cli.run_index --deal Blackbay_III
"""

from pathlib import Path
import argparse
from veridian_atlas.data_pipeline.processors.index_builder import build_chroma_index

DEALS_BASE = Path("veridian_atlas/data/deals")
DB_PATH = Path("veridian_atlas/data/indexes/chroma_db")


# -----------------------------------------------------
# PROGRAMMATIC ENTRYPOINT
# -----------------------------------------------------


def run(deal: str | None = None, reset: bool = False) -> dict:
    """
    Build vector index(es) and generate embeddings implicitly.
    Returns dict of {deal_name: status}.
    """
    return _index_single(deal, reset) if deal else _index_all(reset)


# -----------------------------------------------------
# INDEX BUILDING (SINGLE DEAL)
# -----------------------------------------------------


def _index_single(deal: str, reset: bool) -> dict:
    chunks_path = DEALS_BASE / deal / "processed" / "chunks.jsonl"

    if not chunks_path.exists():
        raise FileNotFoundError(
            f"[ERROR] Missing chunks.jsonl: {chunks_path}\n"
            f"Run chunker first (run_chunker.run())."
        )

    print("\n--------------------------------------------------")
    print(f"[INDEX] DEAL:          {deal}")
    print(f"[COLLECTION NAME]:     VA_{deal}")
    print(f"[CHUNKS SOURCE]:       {chunks_path}")
    print(f"[DB PATH]:             {DB_PATH}")
    print(f"[RESET BEFORE BUILD]:  {'YES' if reset else 'NO'}")
    print("--------------------------------------------------\n")

    build_chroma_index(
        deal_name=deal,
        chunks_path=chunks_path,
        db_path=DB_PATH,
        reset_existing=reset,
    )

    print(f"✔ Index built for: {deal}")
    return {deal: "indexed"}


# -----------------------------------------------------
# INDEX BUILDING (ALL DEALS)
# -----------------------------------------------------


def _index_all(reset: bool) -> dict:
    print("\n=== BATCH INDEX BUILD START ===")

    reset_first = reset
    results = {}

    for deal_dir in DEALS_BASE.iterdir():
        if not deal_dir.is_dir():
            continue

        deal = deal_dir.name
        chunks_file = deal_dir / "processed" / "chunks.jsonl"

        if chunks_file.exists():
            result = _index_single(deal, reset=reset_first)
            results.update(result)
            reset_first = False  # Only reset on the first build
        else:
            print(f"[SKIP] Missing chunks for: {deal}")
            results[deal] = "skipped"

    print("\n=== BATCH COMPLETE | VECTOR DB READY ===\n")
    return results


# -----------------------------------------------------
# CLI MODE
# -----------------------------------------------------


def get_args():
    parser = argparse.ArgumentParser(
        description="Build ChromaDB vector indexes for one or all deals."
    )
    parser.add_argument("--deal", type=str, help="Deal to index (e.g. Blackbay_III)")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset DB before initial index build (not repeated in batch mode)",
    )
    return parser.parse_args()


def main():
    args = get_args()
    results = run(deal=args.deal, reset=args.reset)
    print("[READY] Vector DB prepared for RAG.\n")
    print("RESULTS:", results)


if __name__ == "__main__":
    main()
