"""
text_loader.py
--------------
TXT ingestion pipeline for Veridian Atlas.

Enhancements:
- Receives SHA-256 hash from router
- Adds "source_format": "txt" to output
- Clean clause + section segmentation
"""

import re
from pathlib import Path
from typing import List
from veridian_atlas.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------
# Basic file utilities
# ---------------------------------------------------------
def extract_content(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning(f"[TEXT] UTF-8 failed; retry cp1252: {file_path.name}")
        return file_path.read_text(encoding="cp1252")
    except Exception as exc:
        logger.exception(f"[TEXT] Read error: {exc}")
        return ""


def normalize_text(content: str) -> str:
    return content.replace("\r\n", "\n").replace("\r", "\n").strip()


# ---------------------------------------------------------
# Patterns
# ---------------------------------------------------------
SEPARATOR_PATTERN = re.compile(r"(?m)^\s*[-_=]{5,}\s*$")
SECTION_PATTERN = re.compile(
    r"(?m)^(SECTION\s+[0-9]+)\s*(?:[-–]\s*(.*))?$",
    flags=re.IGNORECASE
)
CLAUSE_PATTERN = re.compile(r"(?m)^[0-9]+(?:\.[0-9]+)+(?:\([a-z]\))?")


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def clean_block(text: str) -> str:
    text = SEPARATOR_PATTERN.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_sections(normalized: str) -> List[dict]:
    matches = list(SECTION_PATTERN.finditer(normalized))
    if not matches:
        logger.warning("[TEXT] No section headers detected.")
        return []

    out = []
    for i, m in enumerate(matches):
        start, end = m.end(), matches[i + 1].start() if i < len(matches) - 1 else len(normalized)
        out.append({
            "section_id": m.group(1).strip(),
            "section_title": (m.group(2) or "").strip(),
            "raw_section_text": normalized[start:end].strip(),
            "section_start": start,
            "section_end": end,
        })
    return out


def extract_clauses(raw: str) -> List[dict]:
    matches = list(CLAUSE_PATTERN.finditer(raw))
    if not matches:
        return []

    clauses = []
    for i, m in enumerate(matches):
        next_start = matches[i + 1].start() if i < len(matches) - 1 else len(raw)
        line = raw[m.start():raw.find("\n", m.end())].strip()

        parts = line.split(" ", 1)
        cid = parts[0]
        ctitle = parts[1].strip() if len(parts) > 1 else ""

        body = raw[m.end():next_start]
        body = clean_block(body.replace(line, "").strip()) or ctitle

        clauses.append({
            "clause_id": cid,
            "clause_title": ctitle,
            "clause_text": body,
        })

    return clauses


# ---------------------------------------------------------
# Main entry point
# ---------------------------------------------------------
def handle_text_loading(
    deal_name: str,
    doc_id: str,
    file_path: Path,
    file_hash: str
) -> List[dict]:

    logger.info(f"[TEXT] Loading TXT → {file_path.name} | Deal={deal_name} | Doc={doc_id}")

    raw = extract_content(file_path)
    if not raw:
        return []

    normalized = normalize_text(raw)
    sections = extract_sections(normalized)

    final = []
    for s in sections:
        cleaned = clean_block(re.sub(
            r"(?m)^[0-9]+(?:\.[0-9]+)+(?:\([a-z]\))?\s*",
            "",
            s["raw_section_text"]
        ))

        final.append({
            "deal_name": deal_name,
            "document_id": doc_id,
            "section_id": s["section_id"],
            "section_title": s["section_title"],
            "section_text": cleaned,
            "clauses": extract_clauses(s["raw_section_text"]),
            "location": {"start": s["section_start"], "end": s["section_end"]},
            "source_meta": {
                "file_type": "txt",
                "source_format": "txt",                   # <-- NEW
                "file_hash": file_hash,                   # <-- NEW
                "parser_version": "v2-multideal",
            },
        })

    logger.info(f"[TEXT] Parsed {len(final)} sections | Doc={doc_id}")
    return final
