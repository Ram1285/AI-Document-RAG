from uuid import uuid4


def chunk_pages(
    document_id: str,
    pages: list[dict],
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> list[dict]:
    chunks = []

    for page in pages:
        text = page["text"]
        start = 0
        page_chunks = []

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                page_chunks.append(chunk_text)
            if end == len(text):
                break
            start = max(0, end - chunk_overlap)

        for chunk_text in page_chunks:
            chunks.append(
                {
                    "id": uuid4().hex,
                    "document_id": document_id,
                    "chunk_index": len(chunks),
                    "page_number": page["page_number"],
                    "text": chunk_text,
                }
            )

    return chunks
