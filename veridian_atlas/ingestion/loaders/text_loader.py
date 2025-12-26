from veridian_atlas.utils.logger import get_logger

logger = get_logger(__name__)

def handle_text_loading(file_path):
    content = extract_content(file_path)
    if not content:
        logger.error("No content found in file")

    logger.info("Content extracted")

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