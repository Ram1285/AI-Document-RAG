from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.models.database import init_db


def test_upload_pdf_saves_file():
    init_db()
    upload_dir = Path("data/test-uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = None

    def override_settings():
        settings = get_settings()
        return settings.model_copy(update={"upload_dir": upload_dir})

    app.dependency_overrides[get_settings] = override_settings

    client = TestClient(app)
    try:
        response = client.post(
            "/documents/upload?process=false",
            files={"file": ("sample.pdf", b"%PDF-1.4 test content", "application/pdf")},
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["message"] == "Document uploaded successfully"
        stored_filename = payload["document"]["stored_filename"]
        stored_path = upload_dir / stored_filename
        assert stored_filename.endswith(".pdf")
        assert stored_path.exists()
    finally:
        app.dependency_overrides.clear()
        if stored_path:
            stored_path.unlink(missing_ok=True)



def test_upload_rejects_unsupported_file_type():
    init_db()
    client = TestClient(app)
    response = client.post(
        "/documents/upload?process=false",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
