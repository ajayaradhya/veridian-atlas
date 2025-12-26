from veridian_atlas.utils.logger import get_logger
from pathlib import Path

logger = get_logger(__name__)# Handles picking file and calling relevant loader based on extention

from veridian_atlas.ingestion.loaders import text_loader

# As of now hardcoded
deal_name = "Blackbay_III"

# Check if "raw" folder has documents
raw_path = "raw"
path_to_check = f"veridian_atlas/data/deals/{deal_name}/{raw_path}"

full_path = Path.cwd() / path_to_check

if not full_path.exists():
    logger.info(f"Does not exist. Path: {full_path}")

logger.info(f"Path exists: {full_path}")

# Raw documents retrieval from the path
for file_path in full_path.iterdir():
    if file_path.is_file():
        logger.info(f"File found: {file_path.name}")
        file_name, extension = file_path.name.split(".")
        if extension == "txt":
            logger.info("TXT file found. We will use text_loader")
            text_loader.handle_text_loading(file_path)
        else:
            logger.error("Not yet implemented")
            raise NotImplementedError(f"{extension} not implemented yet")