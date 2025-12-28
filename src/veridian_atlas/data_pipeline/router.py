"""
router.py
----------
Multi-deal ingestion router for Veridian Atlas.

Directory Standard:
veridian_atlas.data.deals.{deal_name}.raw/*.txt
veridian_atlas.data.deals.{deal_name}.processed/sections.json

Features:
- Multi-document routing
- SHA256 hashing for version tracking
- Overwrites processed/sections.json on each ingest
- Loader map is future-proof for PDF/DOCX
"""

from pathlib import Path
from typing import Dict, List, Optional, Callable
import hashlib
import json

from veridian_atlas.utils.logger import get_logger
from veridian_atlas.data_pipeline.loaders.text_loader import handle_text_loading

logger = get_logger(__name__)

# ---------------------------------------------------------
# Loader registry (extendable)
# ---------------------------------------------------------
LOADER_MAP: Dict[str, Callable] = {
    ".txt": handle_text_loading,
    # ".pdf": handle_pdf_loading,
    # ".docx": handle_docx_loading,
}

# Base deal path (new folder standard)
BASE_DEALS_PATH = Path(__file__).resolve().parent.parent / "data" / "deals"


# ---------------------------------------------------------
# SHA-256 hashing for file version detection
# ---------------------------------------------------------
def compute_file_hash(file_path: Path) -> str:
    """Computes sha256 checksum for version identity and cache validation."""
    sha = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


# ---------------------------------------------------------
# Route a single file
# ---------------------------------------------------------
def route_file(file_path: Path, deal_name: str, doc_id: Optional[str] = None) -> List[dict]:
    if not file_path.exists():
        logger.error(f"[ROUTER] Missing file → {file_path}")
        return []

    ext = file_path.suffix.lower()
    doc_id = doc_id or file_path.stem

    logger.info(f"[ROUTER] Processing → {file_path.name} | Deal={deal_name} | Doc={doc_id}")

    if ext not in LOADER_MAP:
        logger.error(f"[ROUTER] Unsupported file type '{ext}' | File={file_path.name}")
        raise ValueError(f"Unsupported extension: {ext}")

    file_hash = compute_file_hash(file_path)

    try:
        loader = LOADER_MAP[ext]
        return loader(deal_name=deal_name, doc_id=doc_id, file_path=file_path, file_hash=file_hash)
    except Exception as exc:
        logger.exception(f"[ROUTER] Loader crash → {file_path.name}: {exc}")
        return []


# ---------------------------------------------------------
# Deal-level ingestion
# ---------------------------------------------------------
def ingest_deal(deal_name: str) -> Dict[str, List[dict]]:
    raw_path = BASE_DEALS_PATH / deal_name / "raw"
    processed_path = BASE_DEALS_PATH / deal_name / "processed"
    output_file = processed_path / "sections.json"

    logger.info("\n==============================")
    logger.info(f"[DEAL] Ingesting {deal_name}")
    logger.info("==============================")
    logger.info(f"[DEAL] RAW: {raw_path}")

    if not raw_path.exists():
        logger.error(f"[DEAL] Raw directory missing → {raw_path}")
        return {}

    results = {}
    for file in raw_path.iterdir():
        if file.is_file():
            doc_id = file.stem
            results[doc_id] = route_file(file, deal_name, doc_id)

    # Ensure processed folder
    processed_path.mkdir(parents=True, exist_ok=True)

    # Write output JSON
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"[DEAL] ✔ Saved → {output_file}")
    except Exception as exc:
        logger.exception(f"[DEAL] FAILED writing output: {exc}")

    return results


# ---------------------------------------------------------
# Global multi-deal ingest
# ---------------------------------------------------------
def ingest_all_deals() -> Dict[str, Dict[str, List[dict]]]:
    logger.info("[GLOBAL] Starting multi-deal ingestion...")

    if not BASE_DEALS_PATH.exists():
        logger.error(f"[GLOBAL] Deals directory missing: {BASE_DEALS_PATH}")
        return {}

    deals = {}
    for deal_folder in BASE_DEALS_PATH.iterdir():
        if deal_folder.is_dir():
            deal_name = deal_folder.name
            deals[deal_name] = ingest_deal(deal_name)

    logger.info(f"[GLOBAL] Completed ingestion for {len(deals)} deals.")
    return deals


def supported_extensions() -> list[str]:
    return list(LOADER_MAP.keys())
