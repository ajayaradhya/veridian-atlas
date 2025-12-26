"""
text_loader.py
--------------
TXT ingestion pipeline for Veridian Atlas.

Fixes Added:
- Remove decorative separators ("-----") from section and clause text
- Prevent title duplication inside clause text
- Normalize output so clause text does not begin with the clause header again
"""

import re
from pathlib import Path
from veridian_atlas.utils.logger import get_logger

logger = get_logger(__name__)


# -------------------------------------------------------
# 1) LOAD + NORMALIZE
# -------------------------------------------------------

def extract_content(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning(f"UTF-8 failed for {file_path.name}, using cp1252...")
        return file_path.read_text(encoding="cp1252")


def normalize_text(content: str) -> str:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    content = content.strip()
    return content


# -------------------------------------------------------
# 2) FILTER NOISE / VISUAL SEPARATORS
# -------------------------------------------------------

SEPARATOR_PATTERN = re.compile(r"^-{8,}|^_{8,}|^=+$", re.MULTILINE)

def clean_block(text: str) -> str:
    """Remove decorative separator lines and clean whitespace."""
    text = SEPARATOR_PATTERN.sub("", text)          # remove ----- lines
    text = re.sub(r"\n{3,}", "\n\n", text)          # collapse extra blank lines
    return text.strip()


# -------------------------------------------------------
# 3) SECTION EXTRACTION
# -------------------------------------------------------

SECTION_PATTERN = re.compile(r"(?m)^(SECTION\s+[0-9]+)(?:\s*–\s*(.*))?$")

def extract_sections(normalized: str) -> list[dict]:
    matches = list(SECTION_PATTERN.finditer(normalized))
    if not matches:
        logger.warning("No SECTION patterns found.")
        return []

    sections = []

    for m in matches:
        heading_start, heading_end = m.start(), m.end()
        full_line = m.group(0).strip()
        section_id = m.group(1).strip()
        title = m.group(2).strip() if m.group(2) else ""

        sections.append({
            "id": section_id,
            "title": title,
            "start": heading_start,
            "end": heading_end
        })

    structured = []
    for i, sec in enumerate(sections):
        start = sec["end"]
        end = sections[i+1]["start"] if i < len(sections)-1 else len(normalized)
        content = normalized[start:end]
        content = clean_block(content)  # FIX APPLIED

        structured.append({
            "section_id": sec["id"],
            "section_title": sec["title"],
            "section_text": content,
            "section_start": start,
            "section_end": end
        })

    return structured


# -------------------------------------------------------
# 4) CLAUSE EXTRACTION (NO DUPLICATE TITLES)
# -------------------------------------------------------

CLAUSE_PATTERN = re.compile(r"(?m)^[0-9]+\.[0-9]+")

def extract_clauses(section_text: str) -> list[dict]:
    matches = list(CLAUSE_PATTERN.finditer(section_text))
    if not matches:
        return []

    clause_headers = []
    for m in matches:
        c_start, c_end = m.start(), m.end()
        line_start = section_text.rfind("\n", 0, c_start) + 1
        line_end = section_text.find("\n", c_end)
        full_line = section_text[line_start:line_end].strip()

        parts = full_line.split(" ", 1)
        clause_id = parts[0].strip()
        clause_title = parts[1].strip() if len(parts) > 1 else ""

        clause_headers.append({
            "id": clause_id,
            "title": clause_title,
            "start": c_start,
            "end": c_end,
            "full_header": full_line
        })

    items = []
    for i, h in enumerate(clause_headers):
        text_start = h["end"]
        text_end = clause_headers[i+1]["start"] if i < len(clause_headers)-1 else len(section_text)

        # raw chunk
        text_chunk = section_text[text_start:text_end].strip()

        # FIX 1: remove full clause header from body if repeated
        if text_chunk.startswith(h["full_header"]):
            text_chunk = text_chunk[len(h["full_header"]):].strip()

        # FIX 2: remove repeated title if duplicated
        if h["title"] and text_chunk.startswith(h["title"]):
            text_chunk = text_chunk[len(h["title"]):].strip()

        # FIX 3: remove separators
        text_chunk = clean_block(text_chunk)

        items.append({
            "clause_id": h["id"],
            "clause_title": h["title"],
            "clause_text": text_chunk,
            "clause_start": text_start,
            "clause_end": text_end
        })

    return items


# -------------------------------------------------------
# 5) RETURN UNIFIED STRUCTURE
# -------------------------------------------------------

def format_sections(deal_name: str, sections: list[dict]) -> list[dict]:
    output = []
    for sec in sections:
        clauses = extract_clauses(sec["section_text"])
        output.append({
            "deal_name": deal_name,
            "section_id": sec["section_id"],
            "section_title": sec["section_title"],
            "section_text": clean_block(sec["section_text"]),   # FIX
            "clauses": clauses,
            "location": {
                "section_start": sec["section_start"],
                "section_end": sec["section_end"]
            }
        })
    return output


# -------------------------------------------------------
# 6) ENTRYPOINT
# -------------------------------------------------------

def handle_text_loading(deal_name: str, file_path: Path) -> list[dict]:
    logger.info(f"Loading TXT: {file_path.name}")

    raw = extract_content(file_path)
    normalized = normalize_text(raw)

    sections = extract_sections(normalized)
    if not sections:
        logger.warning(f"No sections extracted from: {file_path.name}")
        return []

    result = format_sections(deal_name, sections)
    logger.info(f"Parsed {len(result)} clean sections from {file_path.name}")
    return result
