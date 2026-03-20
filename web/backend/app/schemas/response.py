"""Response schemas."""
from pydantic import BaseModel, Field


class StandardParseResult(BaseModel):
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    warnings: list[str] = []
    missing_fields: list[str] = []


class ParseResponse(BaseModel):
    success: bool = True
    preview_columns: list[str] = []
    preview_rows: list[dict[str, str]] = []
    warnings: list[str] = []
    missing_fields: list[str] = []
    download_id: str | None = None
    error_code: str | None = None
    message: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
