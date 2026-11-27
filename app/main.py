from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

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


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


app.include_router(documents_router)
app.include_router(rag_router)
