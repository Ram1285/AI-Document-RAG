from sqlalchemy.orm import Session

from app.models.entities import Chunk, Document


def create_document(db: Session, document_data: dict) -> Document:
    document = Document(
        id=document_data["document_id"],
        original_filename=document_data["original_filename"],
        stored_filename=document_data["stored_filename"],
        local_path=document_data["local_path"],
        content_type=document_data["content_type"],
        size_bytes=document_data["size_bytes"],
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update_document_processed(db: Session, document_id: str, page_count: int, chunk_count: int) -> Document:
    document = get_document(db, document_id)
    document.status = "processed"
    document.page_count = page_count
    document.chunk_count = chunk_count
    db.commit()
    db.refresh(document)
    return document


def get_document(db: Session, document_id: str) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise ValueError("Document not found")
    return document


def list_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()


def replace_chunks(db: Session, document_id: str, chunks: list[dict]) -> None:
    db.query(Chunk).filter(Chunk.document_id == document_id).delete()
    for chunk in chunks:
        db.add(
            Chunk(
                id=chunk["id"],
                document_id=document_id,
                chunk_index=chunk["chunk_index"],
                page_number=chunk["page_number"],
                text=chunk["text"],
            )
        )
    db.commit()


def get_chunk(db: Session, chunk_id: str) -> Chunk | None:
    return db.get(Chunk, chunk_id)
