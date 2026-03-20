"""Request schemas."""
from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    document_type: str = Field(default="auto_detect", description="auto_detect, shipping_document, invoice, packing_list, bill_of_lading, custom")
    target_columns: str = Field(default="", description="JSON array string or comma-separated")
    scene_description: str = Field(default="", description="Domain context for extraction")
    translation_rules: str = Field(default="", description="key=value per line or JSON dict string")
    sheet_title: str = Field(default="Extraction Result", max_length=50)
