# -*- coding: utf-8 -*-
"""集中配置（路径/模型/词库等）。"""

import os
import logging

logger = logging.getLogger(__name__)

# ===== GLM =====
GLM_API_KEY = os.environ.get("GLM_API_KEY", "")
if not GLM_API_KEY:
    logger.warning("GLM_API_KEY 未设置。某些功能可能不可用。")

GLM_MODEL_VISION = "GLM-4.6V"
GLM_MODEL_TEXT = "GLM-5"

# ===== RAG 词库 =====
RAG_PDF_PATH = "/Users/tankaixi/Desktop/招商青岛POC/RAG库/船舶实用英语手册机电分册最新版.pdf"
VOCAB_JSON_PATH = "/Users/tankaixi/Desktop/招商青岛POC/RAG库/vocab_dict.json"

# ===== Pipeline 默认 =====
DOMAIN_CONTEXT = "这是招商工业港口物流单/发票箱单场景，内容多为船舶机电/消防系统/备件等术语。"

# 输出目录规则：PDF同目录下建立 <PDF名>Image
IMAGE_FOLDER_SUFFIX = "Image"
