from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import require_api_key
from app.models.database import get_db
from app.models.schemas import DocumentOut
from app.services.cloud_storage import upload_file_to_s3
from app.services.document_storage import save_uploaded_document
from app.services.rag import process_document
from app.services.repository import create_document, get_document, list_documents

router = APIRouter(prefix="/documents", tags=["documents"], dependencies=[Depends(require_api_key)])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    process: bool = Query(default=True),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> dict:
    try:
        saved_document = await save_uploaded_document(
            file=file,
            upload_dir=settings.upload_dir,
            max_size_mb=settings.max_upload_size_mb,
        )
        document = create_document(db, saved_document)
        s3_uri = upload_file_to_s3(document.local_path)
        processing = None
        if process:
            processing = process_document(db, document.id, document.local_path)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "message": "Document uploaded successfully",
        "document": {
            "id": document.id,
            "original_filename": document.original_filename,
            "stored_filename": document.stored_filename,
            "status": "processed" if processing else document.status,
            "page_count": processing["page_count"] if processing else document.page_count,
            "chunk_count": processing["chunk_count"] if processing else document.chunk_count,
            "s3_uri": s3_uri,
        },
    }


@router.get("", response_model=list[DocumentOut])
def get_documents(db: Session = Depends(get_db)) -> list:
    return list_documents(db)


@router.get("/{document_id}", response_model=DocumentOut)
def get_document_by_id(document_id: str, db: Session = Depends(get_db)):
    try:
        return get_document(db, document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
