import json
from pathlib import Path
from veridian_atlas.ingestion.router import route_folder

deal = "Blackbay_III"
raw_folder = Path(f"veridian_atlas/data/deals/{deal}/raw")
processed_folder = Path(f"veridian_atlas/data/deals/{deal}/processed")

deal_meta_data = route_folder(deal, folder_path=raw_folder)
with open(processed_folder / "section.json", "w") as f:
    json.dump(deal_meta_data, f, indent=4)