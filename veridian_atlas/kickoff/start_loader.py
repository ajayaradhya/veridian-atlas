"""
start_loader.py
----------------
Bootstraps ingestion for the new directory design.
"""

import argparse
from veridian_atlas.ingestion.router import ingest_all_deals, ingest_deal, supported_extensions
from veridian_atlas.utils.logger import get_logger

logger = get_logger(__name__)


def get_args():
    p = argparse.ArgumentParser(description="Run Veridian Atlas ingestion.")
    p.add_argument("--deal", type=str, help="Ingest only a specific deal.")
    return p.parse_args()


def main():
    args = get_args()

    logger.info("============================================")
    logger.info("     VERIDIAN ATLAS INGESTION EXECUTION     ")
    logger.info("============================================")
    logger.info(f"Supported types: {supported_extensions()}")

    if args.deal:
        logger.info(f"[MODE] Single-deal ingest → {args.deal}")
        ingest_deal(args.deal)
    else:
        logger.info("[MODE] All deals ingest")
        ingest_all_deals()

    logger.info("[DONE] Ingestion complete.")


if __name__ == "__main__":
    main()
