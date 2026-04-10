import os
from pathlib import Path
from fastapi import UploadFile
from datetime import datetime

# Resolve absolute path for uploads folder at the project root
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "uploads"

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)

def save_image(file: UploadFile) -> str:
    """Save uploaded image and return file path."""
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())

    return str(filepath)