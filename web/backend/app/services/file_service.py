"""File handling service."""

import os
from fastapi import UploadFile
from typing import Tuple

from app.utils.validators import (
    validate_file_extension,
    validate_vocab_file_extension,
    validate_file_size,
    validate_file_empty,
)
from app.utils.temp_files import save_uploaded_file
from app.core.logger import get_logger

logger = get_logger("file_service")


class FileService:
    async def save_and_validate(self, file: UploadFile, file_id: str) -> Tuple[str, str | None]:
        """
        Save uploaded file and validate.
        Returns (file_path, error_message).
        """
        filename = file.filename or "uploaded_file"
        
        # Validate extension
        is_valid, err = validate_file_extension(filename)
        if not is_valid:
            return "", err
        
        # Read content
        content = await file.read()
        
        # Validate size
        is_valid, err = validate_file_size(len(content))
        if not is_valid:
            return "", err
        
        # Validate empty
        is_valid, err = validate_file_empty(len(content))
        if not is_valid:
            return "", err
        
        # Save
        file_path = save_uploaded_file(file_id, filename, content)
        logger.info(f"File saved: {file_path} (size={len(content)})")
        
        return str(file_path), None
    
    async def save_vocab_file(self, file: UploadFile, file_id: str) -> Tuple[str, str | None]:
        """
        Save uploaded vocabulary file and validate.
        Supports PDF, images, Excel, CSV, TXT.
        Returns (file_path, error_message).
        """
        filename = file.filename or "uploaded_vocab"
        
        # Validate extension for vocab files
        is_valid, err = validate_vocab_file_extension(filename)
        if not is_valid:
            return "", err
        
        # Read content
        content = await file.read()
        
        # Validate size
        is_valid, err = validate_file_size(len(content))
        if not is_valid:
            return "", err
        
        # Validate empty
        is_valid, err = validate_file_empty(len(content))
        if not is_valid:
            return "", err
        
        # Save
        file_path = save_uploaded_file(file_id, filename, content)
        logger.info(f"Vocab file saved: {file_path} (size={len(content)})")
        
        return str(file_path), None
