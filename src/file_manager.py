import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIR = PROJECT_ROOT/"data"/"uploads"

UPLOAD_DIR.mkdir(parents = True, exist_ok = True)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "webp", "docx", "csv", "xlsx", "txt" }

def allowed_file(filename):
    if not filename:
        return False
    extension = Path(filename).suffix.lower().replace(".", "")
    return extension in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file is None:
        return None
    
    if not file.filename:
        return None
    
    if not allowed_file(file.filename):
        raise ValueError("Unsupported file type.")
    
    original_name = secure_filename(file.filename)

    unique_name = f"{uuid.uuid4().hex}_{original_name}"

    destination = (UPLOAD_DIR/unique_name)

    file.save(destination)

    return {
        "path": str(destination),
        "filename": original_name,
        "extension": destination.suffix.lower()
    }


    