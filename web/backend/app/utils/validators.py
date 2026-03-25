"""File validators."""

import os
from typing import Optional

# Allowed extensions for document parsing
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}

# Allowed extensions for vocabulary files
VOCAB_ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".xlsx", ".xls", ".txt", ".csv"}

MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB (increased for large dictionary files)


def validate_file_extension(filename: str, allowed_extensions: set = None) -> tuple[bool, Optional[str]]:
    """Check if file extension is allowed. Returns (is_valid, error_message)."""
    allowed = allowed_extensions or ALLOWED_EXTENSIONS
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed:
        return False, f"Unsupported file format: {ext}. Allowed: {', '.join(allowed)}"
    return True, None


def validate_vocab_file_extension(filename: str) -> tuple[bool, Optional[str]]:
    """Check if vocabulary file extension is allowed."""
    return validate_file_extension(filename, VOCAB_ALLOWED_EXTENSIONS)


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
