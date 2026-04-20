import os
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.security import HTTPBearer

from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1", tags=["Upload"])

_bearer = HTTPBearer()

UPLOAD_DIR = "/tmp/uploads"


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    # Intentional path traversal vulnerability: original filename used without sanitization
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(UPLOAD_DIR, file.filename)

    contents = file.file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    return {
        "filename": file.filename,
        "saved_path": save_path,
        "size_bytes": len(contents),
    }
