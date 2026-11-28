# Architecture

```mermaid
flowchart LR
    U[User / Swagger UI] --> API[FastAPI]
    API --> S3[AWS S3]
    API --> DB[(PostgreSQL / RDS)]
    API --> EX[Text Extraction]
    EX --> CH[Chunking]
    CH --> EM[Sentence Transformers]
    EM --> FAISS[(FAISS Vector Store)]
    API --> RAG[RAG Pipeline]
    RAG --> FAISS
    RAG --> OL[Ollama local model]
    OL --> RAG
    RAG -. if Ollama unavailable and key configured .-> GPT[GPT-4o fallback]
    GPT --> RAG
    RAG -. if model calls fail .-> EA[Local extractive fallback]
    EA --> RAG
    RAG --> API
    API --> U
```

## Minimal production mapping

- FastAPI runs in Docker on AWS EC2.
- Docker image is stored in AWS ECR.
- Uploaded files are stored in AWS S3.
- Metadata is stored in AWS RDS PostgreSQL.
- Logs go to CloudWatch through the EC2/Docker logging setup.
- GitHub Actions runs tests and can build/push the image.
