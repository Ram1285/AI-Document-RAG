# AI Document Processing and RAG Platform

A minimal, resume-worthy AI document processing and Retrieval-Augmented Generation platform.

The project demonstrates a practical retrieval-augmented generation pipeline: document text extraction, BAAI BGE embeddings, FAISS semantic retrieval, and local Ollama answer generation.

## Features

- Upload PDF and DOCX documents.
- Store files locally during development.
- Optionally upload files to AWS S3 when `AWS_S3_BUCKET` is configured.
- Extract clean text from PDFs with PyMuPDF and DOCX files with python-docx.
- Split extracted text into overlapping chunks.
- Generate embeddings with BAAI BGE (`BAAI/bge-small-en-v1.5`) through Sentence Transformers.
- Store vectors in FAISS.
- Store document and chunk metadata in SQLAlchemy models.
- Use SQLite locally or PostgreSQL/RDS in cloud deployment.
- Generate answers with a local Ollama model by default, with optional GPT-4o fallback.
- Use local extractive answers if both language model providers are unavailable.
- Search semantically across documents.
- Summarize documents.
- Return source chunks with page references when available.
- Run locally, with Docker, or on AWS EC2.
- Basic optional bearer-token authentication.

## Architecture

```text
User / Swagger UI
  -> FastAPI
  -> Local storage or AWS S3
  -> Text extraction
  -> Chunking
  -> BAAI BGE embeddings
  -> FAISS vector store
  -> RAG pipeline
  -> Ollama local model (primary)
  -> Optional GPT-4o fallback
  -> Local extractive fallback
  -> Answer with source references
```

## Project Structure

```text
app/
  api/              # FastAPI routes
  core/             # config and security
  models/           # SQLAlchemy entities and Pydantic schemas
  services/         # extraction, chunking, embeddings, FAISS, RAG, S3
data/
  uploads/          # local uploaded documents
  processed/        # reserved for extracted text artifacts
vector_store/       # FAISS index and vector metadata
tests/              # automated tests
scripts/            # deployment helper scripts
```

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Run the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

Install and start [Ollama](https://ollama.com/download), then download the default local model:

```powershell
ollama pull llama3.2:1b
```

Keep Ollama running while using the app. It calls the local Ollama server first.

## API Endpoints

- `GET /health`: health check.
- `POST /documents/upload?process=true`: upload and process a PDF/DOCX.
- `GET /documents`: list uploaded documents.
- `GET /documents/{document_id}`: get document metadata.
- `GET /rag/search?query=...`: semantic search.
- `POST /rag/query`: ask a question.
- `POST /rag/summarize`: summarize a document.

Example query body:

```json
{
  "question": "What is this document about?",
  "document_id": "optional-document-id",
  "top_k": 4
}
```

## Environment Variables

Local defaults are in `.env.example`.

Important values:

```text
DATABASE_URL=sqlite:///./data/app.db
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
APP_API_KEY=
AWS_REGION=
AWS_S3_BUCKET=
```

The embedding model is `BAAI/bge-small-en-v1.5`; the app adds BGE's recommended retrieval instruction to short questions but not document chunks. The first use downloads the model. Existing chunks are automatically re-embedded into a separate model-specific FAISS index the next time a question is asked or a document is processed.

Ollama is the primary answer model and runs locally. The default `llama3.2:1b` is a smaller, faster option; change `OLLAMA_MODEL` to `llama3.2` for the larger 3B model. The app keeps Ollama loaded for 30 minutes and limits answer generation to 192 tokens. If Ollama is unavailable, GPT-4o is used only when `OPENAI_API_KEY` is configured; that fallback sends the question and retrieved document text to OpenAI and may incur API charges. If no key is configured or GPT-4o also fails, the app selects relevant sentences locally from the retrieved chunks.

If `APP_API_KEY` is set, call protected endpoints with:

```text
Authorization: Bearer YOUR_KEY
```

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Current tests cover:

- Upload validation.
- Local file saving.
- Chunking with page references.
- Local extractive answer behavior.

## Docker

Build:

```powershell
docker build -t ai-document-rag-platform .
```

Run:

```powershell
docker run --env-file .env -p 8000:8000 ai-document-rag-platform
```

Run with PostgreSQL:

```powershell
docker compose up --build
```

## AWS Deployment

Minimal cloud mapping:

- S3 for document storage.
- EC2 for the Dockerized FastAPI app.
- RDS PostgreSQL for metadata.
- IAM role for least-privilege S3 and CloudWatch access.
- ECR for container image storage.
- CloudWatch for logs.
- GitHub Actions for CI and Docker build.

## Security Notes

- `.env` is ignored by Git.
- Do not commit AWS credentials or API keys.
- Use IAM roles on EC2 instead of static AWS keys.
- Set `APP_API_KEY` for simple API protection.
- Use HTTPS in deployment through Nginx, a load balancer, or a reverse proxy.
- Uploads are limited by file extension and size.

## Resume Description

Built an AI document Q&A RAG platform with Python, BAAI BGE embeddings, FAISS vector search, and local Ollama generation. Implemented PDF/DOCX extraction, overlapping chunking, semantic retrieval, source-grounded answers, and optional GPT-4o fallback.
