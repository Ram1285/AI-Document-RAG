# Interview Guide

## Resume description

Built a Dockerized AI document processing and RAG platform using FastAPI, PyMuPDF, Sentence Transformers, FAISS, PostgreSQL, AWS S3, EC2, RDS, ECR, CloudWatch, and GitHub Actions. The system supports PDF/DOCX upload, text extraction, chunking, embeddings, semantic search, document summarization, question answering, and source/page references.

## How to explain it

The user uploads a PDF or DOCX. The app extracts text, splits it into overlapping chunks, embeds those chunks with Sentence Transformers, and indexes them in FAISS. For a question, it retrieves relevant chunks and sends them as context to the local Ollama model. If Ollama is unavailable, GPT-4o is an optional secondary provider when an API key is configured. If neither model can answer, a local keyword-based extractor selects sentences from the retrieved text.

## Possible interview questions

1. Why did you use FAISS first?
   FAISS is lightweight, local, fast, and good for learning vector search before moving to managed vector databases.

2. Why store metadata in PostgreSQL?
   FAISS stores vectors efficiently, but PostgreSQL is better for structured metadata, document status, filenames, chunk text, and audit records.

3. How do you keep answers grounded?
   The system gives the answer model only the retrieved document context and asks it to answer from that context. The response also includes source chunks for verification; if both models are unavailable, a local extractor returns sentences directly from those chunks.

4. How would you scale it?
   Move files to S3, metadata to RDS, run the API container on EC2 or ECS, use background workers for heavy ingestion, and eventually use a managed vector database.

5. How is security handled?
   Secrets are loaded from environment variables, `.env` is ignored, AWS access should use IAM roles, uploads are validated, and optional bearer-token auth is supported.
