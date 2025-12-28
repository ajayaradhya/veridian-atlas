"""
run_ingestion.py
----------------
CLI + callable ingestion runner.
"""

import argparse
from veridian_atlas.data_pipeline.router import ingest_all_deals, ingest_deal, supported_extensions
from veridian_atlas.utils.logger import get_logger

logger = get_logger(__name__)


def run(deal: str | None = None):
    """
    PROGRAMMATIC INGESTION ENTRYPOINT.
    Use this when calling from Python (ex: run_project.py)
    """
    logger.info("============================================")
    logger.info("     VERIDIAN ATLAS INGESTION EXECUTION     ")
    logger.info("============================================")
    logger.info(f"Supported file types: {supported_extensions()}")

    if deal:
        logger.info(f"[MODE] Single deal ingest → {deal}")
        ingest_deal(deal)
    else:
        logger.info("[MODE] Full ingestion → all deals")
        ingest_all_deals()

    logger.info("[DONE] Ingestion complete.")


def get_args():
    p = argparse.ArgumentParser(description="Run Veridian Atlas ingestion.")
    p.add_argument("--deal", type=str, help="Ingest only a specific deal.")
    return p.parse_args()


def main():
    """
    CLI ENTRYPOINT.
    Calls run() with CLI args.
    """
    args = get_args()
    run(args.deal)


if __name__ == "__main__":
    main()
