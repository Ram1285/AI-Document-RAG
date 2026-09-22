# Stage 2: Local Document Upload

## What we are building

We are adding a minimal FastAPI endpoint that accepts PDF and DOCX files and saves them locally in `data/uploads`.

## Why it is needed

Every document RAG system starts with ingestion. Before extracting text, creating chunks, generating embeddings, or storing vectors, the application needs a safe and predictable way to receive documents.

## Minimum concepts

- `UploadFile`: FastAPI's file upload type.
- `multipart/form-data`: the HTTP format browsers and API clients use for file uploads.
- File validation: checking file extension and file size before accepting data.
- Local storage: a temporary development step before AWS S3 is added.

## Folder/file structure

```text
app/
  main.py
  api/
    documents.py
  core/
    config.py
  services/
    document_storage.py
tests/
  test_document_upload.py
data/
  uploads/
```

## Implementation steps

1. Add app settings in `app/core/config.py`.
2. Add document validation and local saving in `app/services/document_storage.py`.
3. Add the upload route in `app/api/documents.py`.
4. Register the route in `app/main.py`.
5. Add tests for successful upload and unsupported file types.

## How to test it

Run automated tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Use `POST /documents/upload` to upload a `.pdf` or `.docx` file.

## Understand before moving on

Before Stage 3, you should be able to explain:

- Why uploads are validated.
- Why uploaded files get a generated stored filename.
- Why local file storage is useful before AWS S3.
- How FastAPI receives files through `UploadFile`.
