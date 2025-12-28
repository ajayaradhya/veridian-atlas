"""
run_project.py
-----------------------------------------
Primary orchestration script for Veridian Atlas.

Pipeline:
    1. (Optional) Cleanup of generated files
    2. Ingestion  (raw → sections.json)
    3. Chunking   (sections → chunks.jsonl)
    4. Indexing   (embeddings + vector store)
    5. Validation Query

CLI Usage:
    python -m veridian_atlas.cli.run_project
    python -m veridian_atlas.cli.run_project --deal Blackbay_III
    python -m veridian_atlas.cli.run_project --no-validate
    python -m veridian_atlas.cli.run_project --clean
"""

import argparse
from pathlib import Path
from veridian_atlas.cli.run_ingestion import run as run_ingestion
from veridian_atlas.cli.run_chunker import run as run_chunker
from veridian_atlas.cli.run_index import run as run_index
from veridian_atlas.cli.run_query import run as run_query
from veridian_atlas.utils.logger import get_logger

logger = get_logger(__name__)

# Rooted at /src/veridian_atlas/data/deals
DEALS_DIR = Path("veridian_atlas/data/deals")
INDEX_DIR = Path("veridian_atlas/data/indexes/chroma_db")


# ------------------------------------------------------
# CLEANUP HELPERS
# ------------------------------------------------------


def clean_generated(deal: str | None = None):
    """
    Removes previously generated processed files and index artifacts.
    Safe operation: only removes expected files.
    """
    logger.info(">>> CLEANING old generated artifacts...")

    # 1) Clean per-deal processed data
    if deal:
        p = DEALS_DIR / deal / "processed"
        if p.exists():
            for item in p.iterdir():
                item.unlink()
        logger.info(f"[CLEAN] Processed cleared for: {deal}")

    # 2) Clean vector DB (single reset)
    if INDEX_DIR.exists():
        for item in INDEX_DIR.iterdir():
            if item.is_file():
                item.unlink()
            else:
                import shutil

                shutil.rmtree(item)
        logger.info("[CLEAN] ChromaDB index reset.")

    logger.info(">>> CLEAN COMPLETE.\n")


# ------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------


def run_all(
    deal: str | None = None, clean: bool = False, validate: bool = True, reset_index: bool = True
):
    """
    Runs the full pipeline. Batch mode if no deal passed.
    auto-selects first deal for validation if --validate used.
    """

    logger.info("=============================================")
    logger.info(" VERIDIAN ATLAS – FULL PIPELINE EXECUTION ")
    logger.info("=============================================")

    # -- CLEAN FIRST IF REQUESTED
    if clean:
        clean_generated(deal)

    # -- STEP 1: INGESTION
    logger.info("[1/4] INGESTION STARTING...")
    run_ingestion(deal=deal)
    logger.info("[1/4] INGESTION COMPLETE.\n")

    # -- STEP 2: CHUNKING
    logger.info("[2/4] CHUNKING STARTING...")
    run_chunker(deal=deal)
    logger.info("[2/4] CHUNKING COMPLETE.\n")

    # -- STEP 3: VECTOR INDEX BUILD (embeddings implied)
    logger.info("[3/4] INDEX BUILD STARTING...")
    run_index(deal=deal, reset=reset_index)
    logger.info("[3/4] INDEX BUILD COMPLETE.\n")

    # -- STEP 4: OPTIONAL VALIDATION
    if validate:
        logger.info("[4/4] VALIDATION QUERY STARTING...")

        # assign default deal if none provided
        if deal is None:
            available = [d.name for d in DEALS_DIR.iterdir() if d.is_dir()]
            if not available:
                logger.warning("No deals found; skipping validation.")
                return
            deal = available[0]
            logger.warning(f"No deal specified. Using: {deal}")

        test_question = "Summarize the payment obligations."
        response = run_query(test_question, deal=deal)

        logger.info("RAG VALIDATION FEEDBACK")
        logger.info(f"Deal     : {deal}")
        logger.info(f"Question : {test_question}")
        logger.info(f"Answer   : {response.get('answer')}")
        logger.info(f"Citations: {response.get('citations')}\n")

    logger.info("=============================================")
    logger.info("     PIPELINE COMPLETE | SYSTEM READY        ")
    logger.info("=============================================")
    return True


# ------------------------------------------------------
# CLI ARGUMENTS
# ------------------------------------------------------


def get_args():
    parser = argparse.ArgumentParser(description="Run Veridian Atlas full pipeline.")
    parser.add_argument("--deal", type=str, help="Process a single deal.")
    parser.add_argument("--clean", action="store_true", help="Remove generated files first.")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation query.")
    parser.add_argument("--no-reset", action="store_true", help="Do not reset index on rebuild.")
    return parser.parse_args()


def main():
    args = get_args()
    run_all(
        deal=args.deal,
        clean=args.clean,
        validate=not args.no_validate,
        reset_index=not args.no_reset,
    )


if __name__ == "__main__":
    main()
