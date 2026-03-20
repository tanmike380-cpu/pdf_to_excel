"""Download endpoint."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.utils.temp_files import get_excel_path
from app.core.logger import get_logger

logger = get_logger("routes_download")

router = APIRouter()


@router.get("/download/{file_id}")
async def download_excel(file_id: str):
    """
    Download generated Excel file.
    
    Args:
        file_id: UUID of the parse request
    
    Returns:
        Excel file as attachment
    """
    excel_path = get_excel_path(file_id)
    
    if not excel_path.exists():
        logger.warning(f"Excel not found: {file_id}")
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    logger.info(f"Downloading: {excel_path}")
    
    return FileResponse(
        path=excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="extraction_result.xlsx",
    )
