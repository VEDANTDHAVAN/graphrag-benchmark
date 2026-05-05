import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    return text


def extract_pages_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    return pages


def extract_text_from_text_bytes(file_bytes: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return file_bytes.decode(enc)
        except Exception:
            continue
    # fallback: replace undecodable bytes
    return file_bytes.decode("utf-8", errors="replace")


def extract_text_from_file(file_name: str, file_bytes: bytes):
    name = (file_name or "").lower()
    if name.endswith(".pdf"):
        return extract_pages_from_pdf(file_bytes), "pdf"
    if name.endswith(".txt") or name.endswith(".csv"):
        return [extract_text_from_text_bytes(file_bytes)], "text"
    # default: try as text
    return [extract_text_from_text_bytes(file_bytes)], "text"
