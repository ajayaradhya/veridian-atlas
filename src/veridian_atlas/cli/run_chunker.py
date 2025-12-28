"""
start_chunker.py
----------------
CLI + programmatic runner for chunk generation.

Usage (CLI):
    python start_chunker.py --deal AxiomCapital_V
    python start_chunker.py
"""

import argparse
from pathlib import Path
from veridian_atlas.data_pipeline.processors.chunker import (
    chunk_from_file,
    save_chunks_as_jsonl,
    chunk_all_deals,
)

BASE = Path("veridian_atlas/data/deals")


def run(deal: str | None = None) -> dict:
    """
    PROGRAMMATIC ENTRYPOINT.
    Called from run_project.py or other scripts.
    Returns a dict of deal → chunk count.
    """
    results = {}

    if deal:
        section_file = BASE / deal / "processed" / "sections.json"
        output_file = BASE / deal / "processed" / "chunks.jsonl"

        deal_name, chunks = chunk_from_file(section_file)
        save_chunks_as_jsonl(chunks, output_file)

        results[deal_name] = len(chunks)
        print(f"✔ {deal_name}: {len(chunks)} chunks written to {output_file}")
        return results

    # MULTI DEAL MODE
    results = chunk_all_deals()
    print("\n✔ MULTI-DEAL CHUNKING COMPLETE:")
    for d, count in results.items():
        print(f"  - {d}: {count} chunks")

    return results


def get_args():
    p = argparse.ArgumentParser(description="Generate retrieval chunks from processed sections.")
    p.add_argument("--deal", type=str, help="Run chunker for a specific deal only.")
    return p.parse_args()


def main():
    """
    CLI ENTRYPOINT. Wraps run() for terminal usage.
    """
    args = get_args()
    run(args.deal)


if __name__ == "__main__":
    main()
