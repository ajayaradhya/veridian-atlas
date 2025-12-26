from veridian_atlas.utils.logger import get_logger
import re

logger = get_logger(__name__)

def normalize_text(content: str):
    # \r to \n
    content = content.replace("\r", "\n")
    content = content.replace("\r\n", "\n")
    content = content.strip()
    return content

def extract_sections(normalized_content: str):
    # Find section anchors
    section_pattern = re.compile(r"(SECTION\s+[0-9]+)", re.IGNORECASE)
    matches = list(section_pattern.finditer(normalized_content))

    if not matches:
        return []  # no sections found, safe fallback

    sections = []

    # Build metadata for each heading
    for match in matches:
        # Find line containing the heading to get SECTION + TITLE
        line_start = normalized_content.rfind("\n", 0, match.start()) + 1
        line_end   = normalized_content.find("\n", match.end())
        heading_line = normalized_content[line_start:line_end].strip()

        # Split ID vs title if present
        if "–" in heading_line:
            section_id, title = [p.strip() for p in heading_line.split("–", 1)]
        else:
            section_id = heading_line
            title = ""  # title missing or not formatted

        sections.append({
            "id": section_id,
            "title": title,
            "start": match.start(),
            "end": match.end()
        })

    # Extract content between section boundaries
    section_data = []
    for i, sec in enumerate(sections):
        start = sec["end"]
        end = sections[i+1]["start"] if i < len(sections)-1 else len(normalized_content)
        content = normalized_content[start:end].strip("\n ")

        section_data.append({
            "id": sec["id"],
            "title": sec["title"],
            "content": content,
            "content_start": start,
            "content_end": end
        })

    return section_data

def extract_sub_sections(section: dict):
    section_text = section["content"]

    # Identify clause anchors (start of lines containing 1.1 / 2.4 / 2.10 etc.)
    clause_pattern = re.compile(r'(?m)^[0-9]+\.[0-9]+')
    matches = list(clause_pattern.finditer(section_text))

    if not matches:
        return []  # no subsections in this section → return empty list

    clause_headers = []

    # Extract each clause heading and its title (if present)
    for match in matches:
        clause_start = match.start()
        clause_end = match.end()

        # Grab the entire line where the clause appears
        line_start = section_text.rfind("\n", 0, clause_start) + 1
        line_end   = section_text.find("\n", clause_end)
        full_line  = section_text[line_start:line_end].strip()

        # Split `<id> <title>` → "2.10 Maturity Date"
        parts = full_line.split(" ", 1)
        clause_id = parts[0].strip()
        clause_title = parts[1].strip() if len(parts) > 1 else ""

        clause_headers.append({
            "id": clause_id,
            "title": clause_title,
            "start": clause_start,
            "end": clause_end
        })

    # Slice subsection content between clause boundaries (including last)
    subsections = []
    for i, clause in enumerate(clause_headers):
        content_start = clause["end"]
        content_end = clause_headers[i+1]["start"] if i < len(clause_headers)-1 else len(section_text)
        content = section_text[content_start:content_end].strip("\n ")

        subsections.append({
            "id": clause["id"],
            "title": clause["title"],
            "content": content,
            "content_start": content_start,
            "content_end": content_end
        })

    return subsections

def format_sections(deal_name, extracted_sections):
    clauses = []
    for section in extracted_sections:
        sub_sections = extract_sub_sections(section) or []
        for sub_section in sub_sections:
            clauses.append({
                "deal_name": deal_name,
                "section_id": section["id"],
                "clause_id": sub_section["id"],
                "section_title": section["title"],
                "clause_title": sub_section["title"],
                "section_content": section["content"],
                "clause_content": sub_section["content"],
                "location": {
                    "section_start": section["content_start"],
                    "section_end": section["content_end"],
                    "clause_start": sub_section["content_start"],
                    "clause_end": sub_section["content_end"]
                }
            })
        if len(sub_sections) == 0:
            clauses.append({
                "section_id": section["id"],
                "section_title": section["title"],
                "section_content": section["content"],
                "location": {
                    "section_start": section["content_start"],
                    "section_end": section["content_end"],
                }
            })

    return clauses

def extract_content(file_path):
    content = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except UnicodeDecodeError:
        print(f"Error: Could not decode the file '{file_path}' with the specified encoding (utf-8). Will try 'cp1252'")
        try:
            with open(file_path, "r", encoding='cp1252') as f_cp1252:
                content = f_cp1252.read()
        except Exception as exc_cp1252:
            logger.exception(f"Could not decode with 'cp1252' as well. {exc_cp1252}")
            raise
    except Exception as exc:
        logger.exception(f"Could not load file: {file_path}. Error: {exc}")
        raise

    return content

def handle_text_loading(deal_name:str, file_path):
    # Step 1: Extract content
    content = extract_content(file_path)
    if not content:
        logger.error("No content found in file")
    logger.info("Content extracted")

    # Step 2: Normalize text
    normalized_content = normalize_text(content)

    # Step 3: Find patterns and extract sections
    extracted_sections = extract_sections(normalized_content)

    # Step 4: Extract subsections
    list_deal_meta_data = format_sections(deal_name, extracted_sections)
    return list_deal_meta_data