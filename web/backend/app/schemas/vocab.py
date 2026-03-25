"""Vocab schemas for terminology database management."""

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class VocabBuildRequest(BaseModel):
    """Request to build a new vocabulary from a dictionary file."""
    name: str
    description: str = ""
    extraction_prompt: str
    # 提示词描述如何从词典中抽取术语对
    # 例如: "从这本船舶英语手册中抽取所有英文术语和对应的中文翻译"


class VocabEntry(BaseModel):
    """Single vocabulary entry (English -> Chinese)."""
    english: str
    chinese: str
    source: str = ""  # 来源页码或位置


class VocabInfo(BaseModel):
    """Vocabulary metadata."""
    id: str
    name: str
    description: str = ""
    entry_count: int
    created_at: datetime
    file_name: str = ""  # 原始词典文件名


class VocabDetail(VocabInfo):
    """Vocabulary with entries."""
    entries: List[VocabEntry] = []


class VocabListResponse(BaseModel):
    """List of vocabularies."""
    success: bool = True
    vocabularies: List[VocabInfo] = []
    message: str = ""


class VocabBuildResponse(BaseModel):
    """Response after building a vocabulary."""
    success: bool = True
    vocab_id: str = ""
    entry_count: int = 0
    preview_entries: List[VocabEntry] = []  # 前10条预览
    message: str = ""
