# -*- coding: utf-8 -*-
"""根据词汇表，将英文术语映射为中文或中英对照。"""
import os
import json
import re
from typing import Dict, List, Tuple
from config.settings import VOCAB_JSON_PATH

VOCAB_JSON = VOCAB_JSON_PATH


def load_vocab(path: str = VOCAB_JSON) -> Dict[str, str]:
    if not os.path.isfile(path):
        raise SystemExit(f"词汇表未找到，请先运行 build_vocab_from_pdf.py 生成: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
