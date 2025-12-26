"""
router.py
----------
Central ingestion router for Veridian Atlas.
Determines which loader to call based on file extension.

Pipeline:
    (file path) -> detect type -> call loader -> return metadata list
"""

from pathlib import Path
from veridian_atlas.utils.logger import get_logger

from veridian_atlas.ingestion.loaders.text_loader import handle_text_loading

logger = get_logger(__name__)


# -----------------------------
# ROUTER FUNCTION
# -----------------------------
def route_file(file_path: Path, deal_name: str) -> list[dict]:
    """
    Route file to the appropriate loader based on its extension.

    Parameters
    ----------
    file_path : Path
        Full path to the document (raw folder)
    deal_name : str
        The deal identifier (e.g., "Blackbay_III")

    Returns
    -------
    list[dict]
        Parsed metadata (sections, clauses, etc.)
    """

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []

    ext = file_path.suffix.lower()

    logger.info(f"Routing file: {file_path.name} (ext: {ext})")

    # -------------------
    # TEXT FILES
    # -------------------
    if ext == ".txt":
        logger.info("→ TXT detected. Using text_loader.")
        return handle_text_loading(deal_name, file_path)

    # -------------------
    # DOCX FILES
    # -------------------
    if ext == ".docx":
        logger.warning("DOCX ingestion not implemented yet.")
        raise NotImplementedError("DOCX support will be added in ingestion/docs_loader.py")

    # -------------------
    # PDF FILES 
    # -------------------
    if ext == ".pdf":
        logger.warning("PDF ingestion not implemented yet.")
        raise NotImplementedError("PDF support will be added in ingestion/pdf_loader.py")

    # -------------------
    # UNKNOWN FORMAT
    # -------------------
    logger.error(f"Unsupported file type: '{ext}'")
    raise ValueError(f"Unsupported extension: {ext}")


# -----------------------------
# BATCH ROUTER (optional helper)
# -----------------------------
def route_folder(deal_name: str, folder_path: Path) -> dict[str, list[dict]]:
    """
    Iterate through a folder and ingest all supported documents.
    Returns a mapping of filename -> parsed metadata
    """
    logger.info(f"Scanning folder for raw docs: {folder_path}")

    if not folder_path.exists():
        logger.error(f"Folder does not exist: {folder_path}")
        return {}

    results = {}

    for file in folder_path.iterdir():
        if file.is_file():
            try:
                results[file.name] = route_file(file, deal_name)
            except Exception as exc:
                logger.exception(f"Failed to process: {file.name} | Error: {exc}")
                results[file.name] = None  # Track failures rather than hiding them

    return results
