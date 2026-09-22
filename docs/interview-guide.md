# Interview Guide

## Resume description

Built a Dockerized AI document processing and RAG platform using FastAPI, PyMuPDF, Sentence Transformers, FAISS, PostgreSQL, AWS S3, EC2, RDS, ECR, CloudWatch, and GitHub Actions. The system supports PDF/DOCX upload, text extraction, chunking, embeddings, semantic search, document summarization, question answering, and source/page references.

## How to explain it

The user uploads a PDF or DOCX. The API stores the file locally during development and can also upload it to S3 in cloud mode. The app extracts text, splits it into overlapping chunks, generates sentence-transformer embeddings, and stores vectors in FAISS. Metadata such as document ID, filename, chunk text, and page number is stored in PostgreSQL. When a user asks a question, the query is embedded, FAISS retrieves top matching chunks, the context is sent to an LLM, and the API returns an answer with sources.

## Possible interview questions

1. Why did you use FAISS first?
   FAISS is lightweight, local, fast, and good for learning vector search before moving to managed vector databases.

2. Why store metadata in PostgreSQL?
   FAISS stores vectors efficiently, but PostgreSQL is better for structured metadata, document status, filenames, chunk text, and audit records.

3. How do you avoid hallucinations?
   The prompt instructs the LLM to answer only from retrieved context, and the response includes source chunks so users can verify the answer.

4. How would you scale it?
   Move files to S3, metadata to RDS, run the API container on EC2 or ECS, use background workers for heavy ingestion, and eventually use a managed vector database.

5. How is security handled?
   Secrets are loaded from environment variables, `.env` is ignored, AWS access should use IAM roles, uploads are validated, and optional bearer-token auth is supported.
