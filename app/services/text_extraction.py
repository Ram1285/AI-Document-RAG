from pathlib import Path

import fitz
from docx import Document as DocxDocument


def extract_text_by_page(file_path: Path) -> list[dict]:
    extension = file_path.suffix.lower()
    if extension == ".pdf":
        return _extract_pdf(file_path)
    if extension == ".docx":
        return _extract_docx(file_path)
    raise ValueError(f"Unsupported file type for extraction: {extension}")


def _extract_pdf(file_path: Path) -> list[dict]:
    pages = []
    with fitz.open(file_path) as pdf:
        for page_index, page in enumerate(pdf, start=1):
            text = _clean_text(page.get_text("text"))
            if text:
                pages.append({"page_number": page_index, "text": text})
    return pages


def _extract_docx(file_path: Path) -> list[dict]:
    doc = DocxDocument(file_path)
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    cleaned = _clean_text(text)
    return [{"page_number": None, "text": cleaned}] if cleaned else []


def _clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = [line for line in lines if line]
    return "\n".join(cleaned_lines)
