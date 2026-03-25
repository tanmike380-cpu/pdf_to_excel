"""Vocabulary management API routes."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.schemas.vocab import (
    VocabListResponse,
    VocabBuildResponse,
    VocabDetail,
    VocabEntry,
)
from app.services.vocab_service import vocab_service
from app.services.file_service import FileService
from app.services.cleanup_service import cleanup_all
from app.utils.temp_files import generate_uuid
from app.core.logger import get_logger

logger = get_logger("routes_vocab")

router = APIRouter(prefix="/vocab", tags=["Vocabulary"])
file_service = FileService()


@router.get("", response_model=VocabListResponse)
async def list_vocabs():
    """List all available vocabularies."""
    try:
        vocabs = vocab_service.list_vocabs()
        return VocabListResponse(
            success=True,
            vocabularies=vocabs,
            message=f"Found {len(vocabs)} vocabularies",
        )
    except Exception as e:
        logger.exception(f"List vocabs failed: {e}")
        return VocabListResponse(
            success=False,
            message=str(e),
        )


@router.get("/{vocab_id}", response_model=VocabDetail)
async def get_vocab(vocab_id: str):
    """Get vocabulary details by ID."""
    vocab = vocab_service.get_vocab(vocab_id)
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    return vocab


@router.delete("/{vocab_id}")
async def delete_vocab(vocab_id: str):
    """Delete a vocabulary."""
    success = vocab_service.delete_vocab(vocab_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    return {"success": True, "message": f"Vocabulary {vocab_id} deleted"}


@router.post("/build", response_model=VocabBuildResponse)
async def build_vocab(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(default=""),
    extraction_prompt: str = Form(...),
):
    """Build a new vocabulary from a dictionary file."""
    file_id = generate_uuid()
    logger.info(f"Build vocab request: file={file.filename}, name={name}, file_id={file_id}")
    
    response = VocabBuildResponse()
    
    try:
        # Save uploaded file
        file_path, err = await file_service.save_vocab_file(file, file_id)
        if err:
            response.success = False
            response.message = err
            cleanup_all(file_id)
            return response
        
        # Build vocabulary
        vocab_id, entries = vocab_service.build_vocab_from_file(
            file_path=file_path,
            name=name,
            description=description,
            extraction_prompt=extraction_prompt,
            file_name=file.filename or "",
        )
        
        if not vocab_id:
            response.success = False
            response.message = "Failed to extract terminology from file"
            cleanup_all(file_id)
            return response
        
        response.success = True
        response.vocab_id = vocab_id
        response.entry_count = len(entries)
        response.preview_entries = entries[:10]
        response.message = f"Successfully built vocabulary with {len(entries)} entries"
        
        logger.info(f"Vocab built: {vocab_id}, {len(entries)} entries")
        
    except Exception as e:
        logger.exception(f"Build vocab failed: {e}")
        response.success = False
        response.message = str(e)
    
    finally:
        cleanup_all(file_id)
    
    return response


@router.get("/{vocab_id}/dict")
async def get_vocab_dict(vocab_id: str):
    """Get vocabulary as a simple dict (english -> chinese)."""
    vocab_dict = vocab_service.get_vocab_dict(vocab_id)
    if not vocab_dict:
        raise HTTPException(status_code=404, detail="Vocabulary not found or empty")
    return {"success": True, "dict": vocab_dict}
