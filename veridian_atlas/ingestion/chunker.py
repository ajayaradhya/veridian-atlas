"""
chunker.py
----------
Transforms processed sections.json files into retrieval-ready chunks.

Latest Enhancements:
- parent_section normalized to SECTION_### form
- Zero-padded normalized section identifiers
- Added document_display_name (human friendly title)
- Cross-platform path normalization
"""

import json
from pathlib import Path
from typing import Dict, List
from veridian_atlas.utils.logger import get_logger

logger = get_logger(__name__)

BASE_DEALS_PATH = Path("veridian_atlas/data/deals")


# -------------------------------------------------------
# NORMALIZERS
# -------------------------------------------------------

def safe_id(value: str) -> str:
    return str(value).strip().replace(" ", "_").replace("–", "-").replace("—", "-")


def display_name(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def normalize_section(section_id: str) -> str:
    """
    Convert:
       SECTION 1    → SECTION_001
       SECTION 10   → SECTION_010
       SECTION 3.2  → SECTION_003_2
    """
    raw = section_id.replace("SECTION", "").strip()
    parts = raw.replace(".", "_").replace("(", "_").replace(")", "").split("_")

    padded = []
    for p in parts:
        if p.isdigit():
            padded.append(p.zfill(3))
        else:
            padded.append(p)

    return f"SECTION_{'_'.join(padded)}"


# -------------------------------------------------------
# CHUNK ID BUILDERS
# -------------------------------------------------------

def build_section_chunk_id(deal: str, doc: str, normalized_section: str) -> str:
    return f"VA::{safe_id(deal)}::{safe_id(doc)}::{normalized_section}"


def build_clause_chunk_id(deal: str, doc: str, normalized_section: str, clause_id: str) -> str:
    return f"VA::{safe_id(deal)}::{safe_id(doc)}::{normalized_section}::CLAUSE_{safe_id(clause_id)}"


# -------------------------------------------------------
# CORE CHUNK BUILDER
# -------------------------------------------------------

def build_chunks_from_json(parsed_json: Dict, deal_name: str, deal_root: Path) -> List[dict]:
    chunks = []

    for document_id, sections in parsed_json.items():
        raw_source_path = str(deal_root / "raw" / f"{document_id}.txt").replace("\\", "/")
        doc_display = display_name(document_id)

        for sec in sections:
            section_id = sec.get("section_id", "")
            section_title = sec.get("section_title", "").strip()
            section_text = sec.get("section_text", "").strip()
            clauses = sec.get("clauses", [])
            src_meta = sec.get("source_meta", {})

            file_hash = src_meta.get("file_hash")
            source_format = src_meta.get("source_format", "txt")

            # NEW: consistent normalized parent reference
            normalized_section = normalize_section(section_id)
            parent_norm = normalized_section  # ← this is the updated behavior

            # SECTION-LEVEL (no clauses)
            if not clauses:
                chunk_id = build_section_chunk_id(deal_name, document_id, normalized_section)
                chunks.append({
                    "chunk_id": chunk_id,
                    "level": "section",
                    "deal_name": deal_name,
                    "document_id": document_id,
                    "document_display_name": doc_display,
                    "section_id": section_id,
                    "normalized_section": normalized_section,
                    "section_title": section_title,
                    "content": section_text,
                    "metadata": {
                        "origin": "section_no_clauses",
                        "parent_section": parent_norm,            # UPDATED HERE
                        "file_hash": file_hash,
                        "source_format": source_format,
                        "source_path": raw_source_path,
                        "length_chars": len(section_text),
                    },
                })
                continue

            # CLAUSE-LEVEL
            for clause in clauses:
                clause_id = clause.get("clause_id")
                clause_title = clause.get("clause_title", "").strip()
                clause_text = clause.get("clause_text", "").strip()

                chunk_id = build_clause_chunk_id(deal_name, document_id, normalized_section, clause_id)

                chunks.append({
                    "chunk_id": chunk_id,
                    "level": "clause",
                    "deal_name": deal_name,
                    "document_id": document_id,
                    "document_display_name": doc_display,
                    "section_id": section_id,
                    "normalized_section": normalized_section,
                    "clause_id": clause_id,
                    "section_title": section_title,
                    "clause_title": clause_title,
                    "content": clause_text,
                    "metadata": {
                        "origin": "clause",
                        "parent_section": parent_norm,            # UPDATED HERE
                        "file_hash": file_hash,
                        "source_format": source_format,
                        "source_path": raw_source_path,
                        "length_chars": len(clause_text),
                    },
                })

    logger.info(f"[CHUNKER] ✔ Generated {len(chunks)} chunks for deal '{deal_name}'")
    return chunks


# -------------------------------------------------------
# SINGLE DEAL LOAD
# -------------------------------------------------------

def chunk_from_file(section_json_path: Path):
    if not section_json_path.exists():
        raise FileNotFoundError(f"[CHUNKER] sections.json not found: {section_json_path}")

    deal_name = section_json_path.parent.parent.name
    deal_root = section_json_path.parent.parent

    raw = json.loads(section_json_path.read_text(encoding="utf-8"))
    logger.info(f"[LOAD] Deal={deal_name} | Documents={len(raw)}")

    chunks = build_chunks_from_json(raw, deal_name, deal_root)
    return deal_name, chunks


# -------------------------------------------------------
# SAVE JSONL
# -------------------------------------------------------

def save_chunks_as_jsonl(chunks: List[dict], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    logger.info(f"[WRITE] ✔ {len(chunks)} chunks → {output_path}")


# -------------------------------------------------------
# MULTI-DEAL
# -------------------------------------------------------

def chunk_all_deals() -> dict:
    results = {}
    for deal_dir in BASE_DEALS_PATH.iterdir():
        section_json = deal_dir / "processed" / "sections.json"
        if section_json.exists():
            deal, chunks = chunk_from_file(section_json)
            save_chunks_as_jsonl(chunks, deal_dir / "processed" / "chunks.jsonl")
            results[deal] = len(chunks)
    logger.info(f"[GLOBAL] Chunking complete across {len(results)} deals.")
    return results
