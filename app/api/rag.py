from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import require_api_key
from app.models.database import get_db
from app.models.schemas import QueryRequest, QueryResponse, SearchResponse
from app.services.rag import answer_question, semantic_search

router = APIRouter(prefix="/rag", tags=["rag"], dependencies=[Depends(require_api_key)])


@router.post("/query", response_model=QueryResponse)
async def query_documents(payload: QueryRequest, db: Session = Depends(get_db)) -> dict:
    return await answer_question(
        db=db,
        question=payload.question,
        top_k=payload.top_k,
        document_id=payload.document_id,
    )


@router.get("/search", response_model=SearchResponse)
def search_documents(
    query: str = Query(..., min_length=3),
    top_k: int = Query(default=5, ge=1, le=10),
    document_id: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    return {"results": semantic_search(db, query=query, top_k=top_k, document_id=document_id)}


@router.post("/summarize", response_model=QueryResponse)
async def summarize_document(payload: QueryRequest, db: Session = Depends(get_db)) -> dict:
    question = f"Summarize this document: {payload.question}"
    return await answer_question(
        db=db,
        question=question,
        top_k=payload.top_k,
        document_id=payload.document_id,
    )
