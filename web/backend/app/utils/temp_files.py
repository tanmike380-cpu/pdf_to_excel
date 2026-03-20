"""Temporary file management."""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional

# Base directory for temp files (relative to this file)
BASE_DIR = Path(__file__).parent.parent.parent / "outputs"
TEMP_DIR = BASE_DIR / "temp"
EXCEL_DIR = BASE_DIR / "excel"


def ensure_dirs():
    """Ensure temp and excel directories exist."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)


def generate_uuid() -> str:
    """Generate a unique ID for file tracking."""
    return str(uuid.uuid4())


def get_temp_dir(file_id: str) -> Path:
    """Get temp directory for a specific file ID."""
    return TEMP_DIR / file_id


def get_excel_path(file_id: str) -> Path:
    """Get Excel file path for a specific file ID."""
    return EXCEL_DIR / f"{file_id}.xlsx"


def create_temp_dir(file_id: str) -> Path:
    """Create and return temp directory for file ID."""
    ensure_dirs()
    temp_dir = get_temp_dir(file_id)
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def save_uploaded_file(file_id: str, filename: str, content: bytes) -> Path:
    """Save uploaded file to temp directory."""
    temp_dir = create_temp_dir(file_id)
    file_path = temp_dir / filename
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def cleanup_temp_dir(file_id: str):
    """Remove temp directory for file ID."""
    temp_dir = get_temp_dir(file_id)
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


def cleanup_excel_file(file_id: str):
    """Remove Excel file for file ID."""
    excel_path = get_excel_path(file_id)
    if excel_path.exists():
        excel_path.unlink()


def cleanup_all(file_id: str):
    """Clean up all temp files for file ID."""
    cleanup_temp_dir(file_id)
    cleanup_excel_file(file_id)
