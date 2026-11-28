import re
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.chunking import chunk_pages
from app.services.embeddings import embed_texts
from app.services.llm import generate_answer
from app.services.repository import get_chunk, replace_chunks, update_document_processed
from app.services.text_extraction import extract_text_by_page
from app.services.vector_store import FaissVectorStore
from app.models.entities import Chunk


def _get_vector_store(settings) -> FaissVectorStore:
    model_dir = re.sub(r"[^A-Za-z0-9._-]+", "_", settings.embedding_model_name)
    return FaissVectorStore(settings.vector_store_dir / model_dir)


def _ensure_indexed(db: Session, vector_store: FaissVectorStore) -> None:
    if vector_store.size:
        return

    chunks = db.query(Chunk).order_by(Chunk.document_id, Chunk.chunk_index).all()
    if not chunks:
        return

    vectors = embed_texts([chunk.text for chunk in chunks])
    metadata = [
        {
            "document_id": chunk.document_id,
            "chunk_id": chunk.id,
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number,
        }
        for chunk in chunks
    ]
    vector_store.add(vectors, metadata)


def process_document(db: Session, document_id: str, file_path: str) -> dict:
    settings = get_settings()
    pages = extract_text_by_page(Path(file_path))
    chunks = chunk_pages(document_id=document_id, pages=pages)
    replace_chunks(db, document_id, chunks)

    vector_store = _get_vector_store(settings)
    _ensure_indexed(db, vector_store)
    if vector_store.size:
        indexed_ids = {item["chunk_id"] for item in vector_store.metadata}
        new_chunks = [chunk for chunk in chunks if chunk["id"] not in indexed_ids]
    else:
        new_chunks = chunks
    if new_chunks:
        vectors = embed_texts([chunk["text"] for chunk in new_chunks])
        metadata = [
            {
                "document_id": chunk["document_id"],
                "chunk_id": chunk["id"],
                "chunk_index": chunk["chunk_index"],
                "page_number": chunk["page_number"],
            }
            for chunk in new_chunks
        ]
        vector_store.add(vectors, metadata)
    update_document_processed(db, document_id, page_count=len(pages), chunk_count=len(chunks))

    return {"page_count": len(pages), "chunk_count": len(chunks)}


def semantic_search(db: Session, query: str, top_k: int, document_id: str | None = None) -> list[dict]:
    settings = get_settings()
    vector_store = _get_vector_store(settings)
    _ensure_indexed(db, vector_store)
    query_vector = embed_texts([query], is_query=True)
    results = vector_store.search(query_vector, top_k, document_id)

    enriched = []
    for result in results:
        chunk = get_chunk(db, result["chunk_id"])
        if chunk is None:
            continue
        enriched.append(
            {
                "document_id": chunk.document_id,
                "chunk_id": chunk.id,
                "filename": chunk.document.original_filename,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "score": result["score"],
                "text": chunk.text,
            }
        )
    return enriched


async def answer_question(
    db: Session,
    question: str,
    top_k: int,
    document_id: str | None = None,
) -> dict:
    sources = semantic_search(db, query=question, top_k=top_k, document_id=document_id)
    context = "\n\n".join(
        (
            f"Source {index + 1} (page {source['page_number'] or 'n/a'}, "
            f"file: {source['filename']}):\n{source['text']}"
        )
        for index, source in enumerate(sources)
    )
    answer = await generate_answer(question, context)
    return {"answer": answer, "sources": sources}
