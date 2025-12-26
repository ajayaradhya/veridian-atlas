"""
text_loader.py
--------------
TXT ingestion pipeline for Veridian Atlas.

Fix Order Correction:
1. Detect clauses from RAW section block.
2. Extract clause chunks + text.
3. THEN clean section text for section-level summary.
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
        logger.warning(f"[WARN] UTF-8 failed: {file_path.name}, retry cp1252...")
        return file_path.read_text(encoding="cp1252")


def normalize_text(content: str) -> str:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    return content.strip()


# -------------------------------------------------------
# NOISE FILTERS
# -------------------------------------------------------

SEPARATOR_PATTERN = re.compile(r"(?m)^\s*[-_=]{5,}\s*$")

def clean_block(text: str) -> str:
    text = SEPARATOR_PATTERN.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# -------------------------------------------------------
# 2) SECTION EXTRACTION
# -------------------------------------------------------

SECTION_PATTERN = re.compile(
    r"(?m)^(SECTION\s+[0-9]+)\s*(?:[-–]\s*(.*))?$", flags=re.IGNORECASE
)

def extract_sections(normalized: str) -> list[dict]:
    matches = list(SECTION_PATTERN.finditer(normalized))
    if not matches:
        logger.warning("[WARN] No SECTION patterns found.")
        return []

    sections = []
    for m in matches:
        sections.append({
            "id": m.group(1).strip(),
            "title": (m.group(2).strip() if m.group(2) else ""),
            "start": m.start(),
            "end": m.end()
        })

    output = []
    for i, sec in enumerate(sections):
        start = sec["end"]
        end = sections[i+1]["start"] if i < len(sections)-1 else len(normalized)

        raw_section_text = normalized[start:end].strip()

        # DO NOT CLEAN OR REMOVE CLAUSE IDs YET — clause extraction depends on them.
        output.append({
            "section_id": sec["id"],
            "section_title": sec["title"],
            "raw_section_text": raw_section_text,  # keep raw for clause detection
            "section_start": start,
            "section_end": end
        })

    return output


# -------------------------------------------------------
# 3) CLAUSE EXTRACTION (NOW RUNS ON RAW TEXT)
# -------------------------------------------------------

CLAUSE_PATTERN = re.compile(r"(?m)^[0-9]+(?:\.[0-9]+)+(?:\([a-z]\))?")

def extract_clauses(raw: str) -> list[dict]:
    clause_starts = list(CLAUSE_PATTERN.finditer(raw))
    if not clause_starts:
        return []

    headers = []
    for m in clause_starts:
        line_start = raw.rfind("\n", 0, m.start()) + 1
        line_end = raw.find("\n", m.end())
        full_header = raw[line_start:line_end].strip()

        parts = full_header.split(" ", 1)
        clause_id = parts[0]
        clause_title = parts[1].strip() if len(parts) > 1 else ""

        headers.append({
            "id": clause_id,
            "title": clause_title,
            "line_end": line_end,
            "h_start": m.start(),
            "full_header": full_header
        })

    clauses = []
    for i, h in enumerate(headers):
        text_start = h["line_end"]
        text_end = headers[i+1]["h_start"] if i < len(headers)-1 else len(raw)

        body = raw[text_start:text_end].strip()

        if body.startswith(h["full_header"]):
            body = body[len(h["full_header"]):].strip()
        if h["title"] and body.startswith(h["title"]):
            body = body[len(h["title"]):].strip()

        body = clean_block(body)
        if not body:
            body = h["title"]  # fallback

        clauses.append({
            "clause_id": h["id"],
            "clause_title": h["title"],
            "clause_text": body,
            "clause_start": text_start,
            "clause_end": text_end
        })

    return clauses


# -------------------------------------------------------
# 4) STRUCTURED OUTPUT (AFTER CLAUSES ARE TAKEN)
# -------------------------------------------------------

def format_sections(deal_name: str, sections: list[dict]) -> list[dict]:
    final = []
    for sec in sections:

        raw = sec["raw_section_text"]
        clauses = extract_clauses(raw)  # FIXED ORDER: RAW FIRST

        # Now clean section text for high-level summary
        section_summary = re.sub(r"(?m)^[0-9]+(?:\.[0-9]+)+(?:\([a-z]\))?\s*", "", raw)
        section_summary = clean_block(section_summary)

        final.append({
            "deal_name": deal_name,
            "section_id": sec["section_id"],
            "section_title": sec["section_title"],
            "section_text": section_summary,
            "clauses": clauses or [],
            "location": {
                "section_start": sec["section_start"],
                "section_end": sec["section_end"],
            }
        })

    return final


# -------------------------------------------------------
# 5) ENTRY POINT
# -------------------------------------------------------

def handle_text_loading(deal_name: str, file_path: Path) -> list[dict]:
    logger.info(f"[LOAD] TXT → {file_path.name}")

    raw = extract_content(file_path)
    normalized = normalize_text(raw)

    sections = extract_sections(normalized)
    if not sections:
        logger.warning(f"[WARN] Parsing failed on {file_path.name}")
        return []

    data = format_sections(deal_name, sections)
    logger.info(f"[OK] extracted {len(data)} sections ✓")

    return data
