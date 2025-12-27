"""
start_chunker.py
----------------
CLI runner for chunk generation.

Usage:
    # Single deal
    python start_chunker.py --deal AxiomCapital_V

    # All deals
    python start_chunker.py
"""

import argparse
from pathlib import Path
from veridian_atlas.ingestion.chunker import (
    chunk_from_file,
    save_chunks_as_jsonl,
    chunk_all_deals
)

BASE = Path("veridian_atlas/data/deals")


def get_args():
    p = argparse.ArgumentParser(description="Generate retrieval chunks from processed sections.")
    p.add_argument("--deal", type=str, help="Run chunker for a specific deal only.")
    return p.parse_args()


def main():
    args = get_args()

    if args.deal:
        deal = args.deal
        section_file = BASE / deal / "processed" / "sections.json"
        output_file = BASE / deal / "processed" / "chunks.jsonl"

        deal_name, chunks = chunk_from_file(section_file)
        save_chunks_as_jsonl(chunks, output_file)
        print(f"✔ {deal_name}: {len(chunks)} chunks written to {output_file}")

    else:
        results = chunk_all_deals()
        print("\n✔ MULTI-DEAL CHUNKING COMPLETE:")
        for deal, count in results.items():
            print(f"  - {deal}: {count} chunks")


if __name__ == "__main__":
    main()
