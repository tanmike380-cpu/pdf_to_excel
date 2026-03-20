"""Parse service - orchestrates the extraction pipeline."""

from typing import Dict, List, Optional

from app.schemas.response import StandardParseResult
from app.services.algorithm_adapter import run_pipeline
from app.services.excel_service import export_to_excel, get_preview_rows
from app.core.logger import get_logger

logger = get_logger("parse_service")


class ParseService:
    def __init__(self, vocab_path: Optional[str] = None):
        self.vocab_path = vocab_path
    
    def parse(
        self,
        file_path: str,
        document_type: str = "auto_detect",
        target_columns: List[str] = None,
        scene_description: str = "",
        translation_rules: Dict[str, str] = None,
        sheet_title: str = "Extraction Result",
        file_id: str = "",
    ) -> tuple[StandardParseResult, str]:
        """
        Run the full parse pipeline.
        
        Returns:
            (result, excel_path)
        """
        logger.info(f"Parse started: file_id={file_id}")
        
        # Run extraction pipeline
        result = run_pipeline(
            file_path=file_path,
            document_type=document_type,
            target_columns=target_columns,
            scene_description=scene_description,
            translation_rules=translation_rules or {},
            sheet_title=sheet_title,
            vocab_path=self.vocab_path,
        )
        
        # Export to Excel
        excel_path = ""
        if result.rows:
            excel_path = str(export_to_excel(result, file_id, sheet_title))
        
        return result, excel_path
