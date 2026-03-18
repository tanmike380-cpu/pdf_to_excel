# -*- coding: utf-8 -*-
"""RAG 词库构建实现：从中英对照PDF抽取英文->中文词典。

策略：
- 优先用 GLM-4.6V 对渲染后的页面图片抽取 {"英文":"中文"}

注意：该模块只提供“实现函数”，不负责决定是否需要构建（由 build_vocab.py 负责）。
"""

import json
import os
import re
import time
from typing import Dict, Optional

import fitz  # pymupdf
from zai import ZhipuAiClient
from Prompt.prompts import vocab_builder_image_prompt


def page_to_png_bytes(page: fitz.Page, dpi: int = 300) -> bytes:
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    return pix.tobytes("png")


def glm_extract_pairs_from_image(
    png_bytes: bytes,
    client: ZhipuAiClient,
    page_no: int,
    model: str,
) -> Dict[str, str]:
    import base64
    from typing import Any

    img_b64 = base64.b64encode(png_bytes).decode("utf-8")

    prompt = vocab_builder_image_prompt(page_no)

    content = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
        {"type": "text", "text": prompt},
    ]

    resp: Any = None
    retry_waits = [2, 4, 8]
    for attempt in range(len(retry_waits) + 1):
        try:
            print(f"[vocab_builder] 页 {page_no}: stream start")
            stream_resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}],
                thinking={"type": "disabled"},
                stream=True,
                max_tokens=4096,
                temperature=0.1,
                timeout=90,
            )
            raw_parts = []
            streamed_chars = 0
            last_log_ts = time.time()
            for chunk in stream_resp:
                try:
                    choices = getattr(chunk, "choices", None)
                    if not choices:
                        continue
                    delta = getattr(choices[0], "delta", None)
                    piece = getattr(delta, "content", None) if delta is not None else None
                    if piece:
                        raw_parts.append(piece)
                        streamed_chars += len(piece)
                        now = time.time()
                        if now - last_log_ts >= 1.0:
                            print(f"[vocab_builder] 页 {page_no}: streaming chars={streamed_chars}")
                            last_log_ts = now
                except Exception:
                    continue
            resp = "".join(raw_parts)
            print(f"[vocab_builder] 页 {page_no}: stream done chars={len(resp)}")
            break
        except Exception as e:
            msg = str(e)
            if ("429" in msg or "APIReachLimitError" in msg) and attempt < len(retry_waits):
                wait_s = retry_waits[attempt]
                print(f"[vocab_builder] 页 {page_no}: LLM rate limited, retry in {wait_s}s")
                time.sleep(wait_s)
                continue
            print(f"[vocab_builder] 页 {page_no}: LLM request failed: {e}")
            return {}

    raw = str(resp) if resp is not None else ""

    # 兼容模型偶发前后缀文本，提取第一个 JSON 对象
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return {}

    try:
        data = json.loads(m.group(0))
        if not isinstance(data, dict):
            return {}
        cleaned: Dict[str, str] = {}
        for k, v in data.items():
            if not k or not v:
                continue
            eng = str(k).strip()
            zh = str(v).strip()
            # 轻量约束：保证 key 含英文字母、value 含中文
            if not re.search(r"[A-Za-z]", eng):
                continue
            if not re.search(r"[\u4e00-\u9fff]", zh):
                continue
            cleaned[eng] = zh
        return cleaned
    except Exception:
        return {}


def build_vocab_from_pdf(
    pdf_path: str,
    out_json: str,
    api_key: str,
    model: str,
    start_page: int = 1,
    end_page: Optional[int] = None,
) -> Dict[str, str]:
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(pdf_path)

    print(
        f"[vocab_builder] build_vocab_from_pdf: pdf={pdf_path}, out={out_json}, model={model}, start_page={start_page}, end_page={end_page}"
    )

    doc = fitz.open(pdf_path)

    # 1-based -> 0-based idx
    start_idx = max(start_page - 1, 0)
    end_idx = doc.page_count if end_page is None else min(end_page, doc.page_count)

    vocab: Dict[str, str] = {}
    client = ZhipuAiClient(api_key=api_key)

    for i in range(start_idx, end_idx):
        page = doc[i]
        page_no = i + 1

        png_bytes = page_to_png_bytes(page, dpi=300)
        pairs = glm_extract_pairs_from_image(png_bytes, client, page_no, model=model)

        if pairs:
            print(f"[vocab_builder] 页 {page_no}: route=GLM_IMAGE_EXTRACT (pairs={len(pairs)})")
        else:
            print(f"[vocab_builder] 页 {page_no}: route=GLM_IMAGE_EXTRACT_EMPTY")

        if pairs:
            # 不覆盖已有 key，避免反复跑时抖动
            added = 0
            skipped = 0
            for k, v in pairs.items():
                if k not in vocab:
                    vocab[k] = v
                    added += 1
                else:
                    skipped += 1
            print(
                f"[vocab_builder] 页 {page_no}: merge route=DEDUP (added={added}, skipped_existing={skipped}, total={len(vocab)})"
            )
        else:
            print(f"[vocab_builder] 页 {page_no}: route=NO_PAIRS")

        print(f"页 {page_no}: 抽取 {len(pairs)} 条（累计 {len(vocab)}）")

    out_dir = os.path.dirname(out_json)
    if out_dir:
        print(f"[vocab_builder] route=MKDIR out_dir={out_dir}")
        os.makedirs(out_dir, exist_ok=True)
    else:
        print("[vocab_builder] route=NO_OUT_DIR (writing to cwd)")

    print(f"[vocab_builder] route=WRITE_JSON -> {out_json}")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

    print(f"[vocab_builder] done (total_pairs={len(vocab)})")
    return vocab
