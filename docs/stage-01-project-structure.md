# Stage 1: Project Structure

## What we are building

We are creating the base repository structure for a minimal AI Document Processing and RAG platform.

At this stage, the application does not upload, parse, embed, or answer questions yet. The goal is to prepare a clean project foundation.

## Why it is needed

RAG projects can become messy quickly because they include API code, document processing, embeddings, vector search, cloud storage, databases, and deployment files. A simple structure keeps each responsibility in a predictable place.

## Minimum concepts

- `app/api`: HTTP endpoints exposed by FastAPI.
- `app/core`: shared configuration such as environment variables.
- `app/services`: business logic such as text extraction, chunking, embeddings, vector search, and RAG.
- `app/models`: request/response schemas and later database models.
- `data`: local development storage before AWS S3 is added.
- `vector_store`: local FAISS indexes before a more managed vector setup is considered.
- `.env`: local secrets and settings, never committed.

## How to test this stage

Run:

```powershell
Get-ChildItem -Recurse
```

Confirm the folders exist:

- `app`
- `app/api`
- `app/core`
- `app/models`
- `app/services`
- `data/uploads`
- `data/processed`
- `vector_store`
- `tests`
- `docs`
- `scripts`

Then confirm Python can see the package:

```powershell
.\.venv\Scripts\python.exe -c "import app; print('app package ready')"
```

## Understand before moving on

Before Stage 2, you should be able to explain:

- Why source code and local uploaded files are separated.
- Why `.env` is ignored by Git.
- Why we start locally before adding AWS.
- Where API routes, AI logic, and configuration will live.
