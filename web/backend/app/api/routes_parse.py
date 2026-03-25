"""Parse endpoint."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.schemas.response import ParseResponse
from app.services.file_service import FileService
from app.services.parse_service import ParseService
from app.services.excel_service import get_preview_rows
from app.services.cleanup_service import cleanup_all
from app.services.vocab_service import vocab_service
from app.utils.parsers import parse_target_columns, parse_translation_rules, validate_translation_rules_text
from app.utils.temp_files import generate_uuid
from app.core.config import VOCAB_JSON_PATH
from app.core.logger import get_logger

logger = get_logger("routes_parse")

router = APIRouter()

file_service = FileService()
parse_service = ParseService(vocab_path=VOCAB_JSON_PATH if VOCAB_JSON_PATH else None)


@router.post("/parse", response_model=ParseResponse)
async def parse_file(
    file: UploadFile = File(...),
    document_type: str = Form(default="auto_detect"),
    target_columns: str = Form(default=""),
    scene_description: str = Form(default=""),
    translation_rules: str = Form(default=""),
    sheet_title: str = Form(default="Extraction Result"),
    vocab_id: str = Form(default=""),
):
    """
    Parse uploaded file and return structured data.
    
    Args:
        file: Uploaded file (PDF, PNG, JPG, JPEG, TXT)
        document_type: auto_detect, shipping_document, invoice, packing_list, bill_of_lading, custom
        target_columns: JSON array or comma-separated list of column names
        scene_description: Domain context for extraction
        translation_rules: JSON dict or key=value lines for translation (legacy, use vocab_id instead)
        sheet_title: Excel sheet title
        vocab_id: ID of vocabulary to use for translation (recommended)
    
    Returns:
        ParseResponse with preview data and download_id
    """
    file_id = generate_uuid()
    logger.info(f"Parse request: file={file.filename}, doc_type={document_type}, vocab_id={vocab_id}, file_id={file_id}")
    
    response = ParseResponse()
    
    try:
        # Validate translation rules format (if provided)
        rule_errors = validate_translation_rules_text(translation_rules)
        if rule_errors:
            response.success = False
            response.error_code = "INVALID_TRANSLATION_RULES"
            response.message = "; ".join(rule_errors)
            return response
        
        # Save and validate file
        file_path, err = await file_service.save_and_validate(file, file_id)
        if err:
            response.success = False
            response.error_code = "FILE_VALIDATION_ERROR"
            response.message = err
            cleanup_all(file_id)
            return response
        
        # Parse inputs
        columns = parse_target_columns(target_columns)
        rules = parse_translation_rules(translation_rules)
        
        # Load vocabulary if vocab_id provided
        vocab_dict = {}
        if vocab_id:
            vocab_dict = vocab_service.get_vocab_dict(vocab_id)
            if vocab_dict:
                logger.info(f"Loaded vocab {vocab_id}: {len(vocab_dict)} entries")
            else:
                logger.warning(f"Vocab {vocab_id} not found or empty")
        
        # Merge user rules with vocab (user rules take precedence)
        merged_rules = {**vocab_dict, **rules}
        
        # Run pipeline
        result, excel_path = parse_service.parse(
            file_path=file_path,
            document_type=document_type,
            target_columns=columns,
            scene_description=scene_description,
            translation_rules=merged_rules,
            sheet_title=sheet_title,
            file_id=file_id,
        )
        
        # Build response
        response.preview_columns = result.columns
        response.preview_rows = get_preview_rows(result)
        response.warnings = result.warnings
        response.missing_fields = result.missing_fields
        
        if excel_path:
            response.download_id = file_id
        else:
            response.warnings.append("No data extracted, Excel not generated")
        
        # Cleanup temp dir (keep excel)
        cleanup_all(file_id)
        
        logger.info(f"Parse success: {len(result.rows)} rows, file_id={file_id}")
        
    except Exception as e:
        logger.exception(f"Parse failed: {e}")
        response.success = False
        response.error_code = "PARSE_FAILED"
        response.message = str(e)
        cleanup_all(file_id)
    
    return response
