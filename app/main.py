from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.documents import router as documents_router
from app.api.rag import router as rag_router
from app.core.config import get_settings
from app.models.database import init_db
from app.models import entities  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


settings = get_settings()

app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "environment": settings.app_env}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <!doctype html>
    <html>
      <head>
        <title>AI Document RAG Platform</title>
        <style>
          body { font-family: Arial, sans-serif; max-width: 760px; margin: 40px auto; line-height: 1.5; }
          input, textarea, button { width: 100%; padding: 10px; margin: 8px 0; }
          button { cursor: pointer; }
          pre { background: #f4f4f4; padding: 12px; overflow: auto; }
        </style>
      </head>
      <body>
        <h1>AI Document RAG Platform</h1>
        <form action="/documents/upload?process=true" method="post" enctype="multipart/form-data">
          <input name="file" type="file" accept=".pdf,.docx" required />
          <button type="submit">Upload and Process</button>
        </form>
        <p>Use <a href="/docs">Swagger UI</a> for search, Q&A, and summarization endpoints.</p>
      </body>
    </html>
    """


app.include_router(documents_router)
app.include_router(rag_router)
