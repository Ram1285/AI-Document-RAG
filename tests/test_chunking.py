from app.services.chunking import chunk_pages


def test_chunk_pages_preserves_page_reference():
    chunks = chunk_pages(
        document_id="doc-1",
        pages=[{"page_number": 3, "text": "A" * 1200}],
        chunk_size=500,
        chunk_overlap=100,
    )

    assert len(chunks) == 3
    assert chunks[0]["document_id"] == "doc-1"
    assert chunks[0]["page_number"] == 3
    assert chunks[1]["chunk_index"] == 1
