# -*- coding: utf-8 -*-
"""构建/确保 RAG 术语库存在。"""

import os

from config.settings import GLM_API_KEY, GLM_MODEL_VISION
from .vocab_builder import build_vocab_from_pdf


def build_vocab_if_missing(
    rag_pdf: str,
    vocab_json: str,
    start_page: int = 1,
    end_page: int | None = None,
):
    """如果 vocab_json 不存在则从 rag_pdf 构建。"""
    if os.path.isfile(vocab_json) and os.path.getsize(vocab_json) > 10:
        return

    build_vocab_from_pdf(
        pdf_path=rag_pdf,
        out_json=vocab_json,
        api_key=GLM_API_KEY,
        model=GLM_MODEL_VISION,
        start_page=start_page,
        end_page=end_page,
    )
