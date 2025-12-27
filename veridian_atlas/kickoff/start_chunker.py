from pathlib import Path
from veridian_atlas.ingestion.chunker import chunk_from_file, save_chunks_as_jsonl

deal = "Blackbay_III"
section_file = Path(f"veridian_atlas/data/deals/{deal}/processed/sections.json")
output_file  = Path(f"veridian_atlas/data/deals/{deal}/processed/chunks.jsonl")

chunks = chunk_from_file(section_file, deal)
save_chunks_as_jsonl(chunks, output_file)

print(f"Generated {len(chunks)} chunks")
