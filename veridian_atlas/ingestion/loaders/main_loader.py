import json
from veridian_atlas.utils.logger import get_logger
from pathlib import Path

logger = get_logger(__name__)# Handles picking file and calling relevant loader based on extention

from veridian_atlas.ingestion.loaders import text_loader

# As of now hardcoded
deal_name = "Blackbay_III"

# Check if "raw" folder has documents
raw_path = "raw"
processed_path = "processed"
section_clauses_file = "section_clauses.json"
path_to_check = f"veridian_atlas/data/deals/{deal_name}"

raw_folder = Path.cwd() / path_to_check / raw_path

if not raw_folder.exists():
    logger.info(f"Does not exist. Path: {raw_folder}")

logger.info(f"Path exists: {raw_folder}")

# Raw documents retrieval from the path
for file_path in raw_folder.iterdir():
    if file_path.is_file():
        logger.info(f"File found: {file_path.name}")

        # Step 1: Fetch deal meta data from content
        file_name, extension = file_path.name.split(".")
        deal_meta_data = []
        if extension == "txt":
            logger.info("TXT file found. We will use text_loader")
            deal_meta_data = text_loader.handle_text_loading(deal_name, file_path)
        else:
            logger.error("Not yet implemented")
            raise NotImplementedError(f"{extension} not implemented yet")

        # Step 2: Store meta data into processed folder
        if not deal_meta_data:
            continue

        processed_folder = Path.cwd() / path_to_check / processed_path
        if not processed_folder.exists():
            Path.mkdir(processed_folder)
            logger.info("Created 'processed' folder")

        section_file = processed_folder / section_clauses_file
        with open(section_file, "w") as f_sections:
            json.dump(deal_meta_data, f_sections, indent=4)
            logger.info(f"Added section info under {section_file}")
