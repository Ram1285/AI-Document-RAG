from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_document_file(file: UploadFile, max_size_mb: int) -> None:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Unsupported file type. Allowed types: {allowed}")

    max_size_bytes = max_size_mb * 1024 * 1024
    size = getattr(file, "size", None)
    if size is not None and size > max_size_bytes:
        raise ValueError(f"File is too large. Maximum size is {max_size_mb} MB")


async def save_uploaded_document(file: UploadFile, upload_dir: Path, max_size_mb: int) -> dict:
    validate_document_file(file, max_size_mb)
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_filename = Path(file.filename or "document").name
    extension = Path(original_filename).suffix.lower()
    document_id = uuid4().hex
    stored_filename = f"{document_id}{extension}"
    destination = upload_dir / stored_filename

    max_size_bytes = max_size_mb * 1024 * 1024
    bytes_written = 0

    with destination.open("wb") as output_file:
        while chunk := await file.read(1024 * 1024):
            bytes_written += len(chunk)
            if bytes_written > max_size_bytes:
                output_file.close()
                destination.unlink(missing_ok=True)
                raise ValueError(f"File is too large. Maximum size is {max_size_mb} MB")
            output_file.write(chunk)

    return {
        "document_id": document_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "content_type": file.content_type,
        "size_bytes": bytes_written,
        "local_path": str(destination),
    }
