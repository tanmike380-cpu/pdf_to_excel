"""File validators."""

import os
from typing import Optional

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def validate_file_extension(filename: str) -> tuple[bool, Optional[str]]:
    """Check if file extension is allowed. Returns (is_valid, error_message)."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file format: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    return True, None


def validate_file_size(size: int) -> tuple[bool, Optional[str]]:
    """Check if file size is within limit. Returns (is_valid, error_message)."""
    if size > MAX_FILE_SIZE:
        return False, f"File too large: {size / 1024 / 1024:.2f}MB. Max: {MAX_FILE_SIZE / 1024 / 1024}MB"
    return True, None


def validate_file_empty(size: int) -> tuple[bool, Optional[str]]:
    """Check if file is empty. Returns (is_valid, error_message)."""
    if size == 0:
        return False, "File is empty"
    return True, None
