"""
chunker.py
----------
Transforms parsed section/clause JSON into retrieval-ready chunks.

Input  : sections.json (from text_loader/router)
Output : chunks.jsonl (atomic retrieval units)

Changes Added:
- Unified content field: chunk["content"] for all chunks
- Added metadata block for future governance/search
- Added parent_section for clause chunks
- Stable ID generation with whitespace normalization
- Section chunks only when no clauses exist (no duplication)
"""

import json
from pathlib import Path
from veridian_atlas.utils.logger import get_logger

logger = get_logger(__name__)

# -------------------------------------------------------
# HELPER: FORMAT SAFE ID TOKENS
# -------------------------------------------------------

def safe_id(value: str) -> str:
    """Normalize values to ID-friendly tokens."""
    return str(value).strip().replace(" ", "_").replace("–", "-").replace("—", "-")


# -------------------------------------------------------
# ID GENERATORS
# -------------------------------------------------------

def build_section_chunk_id(deal: str, file: str, section_id: str) -> str:
    file_root = safe_id(file.replace(".txt", ""))
    section_norm = safe_id(section_id)
    return f"VA::{deal}::{file_root}::{section_norm}"


def build_clause_chunk_id(deal: str, file: str, section_id: str, clause_id: str) -> str:
    file_root = safe_id(file.replace(".txt", ""))
    section_norm = safe_id(section_id)
    clause_norm = safe_id(clause_id)
    return f"VA::{deal}::{file_root}::{section_norm}::CLAUSE_{clause_norm}"


# -------------------------------------------------------
# CHUNK BUILDER
# -------------------------------------------------------

def build_chunks_from_json(parsed_json: dict, deal_name: str) -> list[dict]:
    chunks = []

    for file_name, sections in parsed_json.items():
        for sec in sections:
            section_id = sec.get("section_id")
            section_title = sec.get("section_title", "").strip()
            section_text = sec.get("section_text", "").strip()
            clauses = sec.get("clauses", [])

            # -------------------------------------------------------
            # SECTION-LEVEL CHUNK (No Clauses)
            # -------------------------------------------------------
            if not clauses:
                chunk_id = build_section_chunk_id(deal_name, file_name, section_id)
                chunks.append({
                    "chunk_id": chunk_id,
                    "level": "section",
                    "deal_name": deal_name,
                    "source_file": file_name,
                    "section_id": section_id,
                    "section_title": section_title,
                    "content": section_text,  # unified text field
                    "metadata": {
                        "parent_section": None,
                        "origin": "section_no_clauses",
                        "length_chars": len(section_text)
                    }
                })
                continue

            # -------------------------------------------------------
            # CLAUSE-LEVEL CHUNKS
            # -------------------------------------------------------
            for clause in clauses:
                clause_id = clause.get("clause_id")
                clause_title = clause.get("clause_title", "").strip()
                clause_text = clause.get("clause_text", "").strip()

                chunk_id = build_clause_chunk_id(deal_name, file_name, section_id, clause_id)

                chunks.append({
                    "chunk_id": chunk_id,
                    "level": "clause",
                    "deal_name": deal_name,
                    "source_file": file_name,
                    "section_id": section_id,
                    "clause_id": clause_id,
                    "section_title": section_title,
                    "clause_title": clause_title,
                    "content": clause_text,  # unified content key
                    "metadata": {
                        "parent_section": section_id,
                        "origin": "clause",
                        "length_chars": len(clause_text)
                    }
                })

    logger.info(f"[CHUNKER] {len(chunks)} chunks generated.")
    return chunks


# -------------------------------------------------------
# ENTRYPOINT (File → Chunks)
# -------------------------------------------------------

def chunk_from_file(section_json_path: Path, deal_name: str) -> list[dict]:
    if not section_json_path.exists():
        raise FileNotFoundError(f"[ERROR] sections.json not found at: {section_json_path}")

    raw = json.loads(section_json_path.read_text(encoding="utf-8"))
    logger.info(f"[LOAD] Loaded sections.json with {len(raw)} top-level document entries.")

    return build_chunks_from_json(raw, deal_name)


# -------------------------------------------------------
# SAVE TO JSONL
# -------------------------------------------------------

def save_chunks_as_jsonl(chunks: list[dict], output_path: Path):
    with open(output_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    logger.info(f"[WRITE] {len(chunks)} chunks → {output_path}")
