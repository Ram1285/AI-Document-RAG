from pydantic import BaseModel, ConfigDict, Field


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    stored_filename: str
    status: str
    page_count: int
    chunk_count: int


class SourceOut(BaseModel):
    document_id: str
    chunk_id: str
    filename: str
    page_number: int | None
    chunk_index: int
    score: float
    text: str


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3)
    document_id: str | None = None
    top_k: int = Field(default=4, ge=1, le=10)


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceOut]


class SearchResponse(BaseModel):
    results: list[SourceOut]
