# -*- coding: utf-8 -*-
"""Images folder -> JSON + Excel (逐张调用 GLM-4.6V).

说明：
- 每张图片单独请求，避免上下文过长。
- 模型输出要求只返回 JSON（数组）。
"""

import base64
import json
import os
import re
import time
from typing import List, Dict, Tuple

import pandas as pd
from zai import ZhipuAiClient
from Prompt.prompts import checklist_extract_prompt
from config.settings import GLM_API_KEY, GLM_MODEL_VISION


def _get_image_files(img_dir: str) -> List[str]:
    exts = {".png", ".jpg", ".jpeg", ".bmp"}
    files = [f for f in os.listdir(img_dir) if os.path.splitext(f)[1].lower() in exts]
    def _sort_key(name: str):
        stem = os.path.splitext(name)[0]
        # page_10 > page_2 的字符串排序问题，改为按页码数字排序
        m = re.search(r"(\d+)$", stem)
        if m:
            return (0, int(m.group(1)), name)
        return (1, 0, name)
    files.sort(key=_sort_key)
    return files


def _doc_name_from_folder(img_dir: str) -> str:
    base = os.path.basename(img_dir)
    return base.removesuffix("Image")


def _prompt(base_doc_name: str, img_file_name: str) -> str:
    _ = img_file_name
    return checklist_extract_prompt(base_doc_name)


def _extract_json_array(raw: str) -> List[Dict]:
    # Packing List 可能很长，这里放宽截取长度，避免数组被截断导致 json.loads 失败
    raw_short = (raw or "")[:50000]

    # 先尝试直接找数组
    m = re.search(r"\[\s*\{[\s\S]*?\}\s*\]", raw_short)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]
        except Exception:
            pass

    # 再尝试找单个对象（模型偶尔会直接给 {..}）
    m = re.search(r"\{[\s\S]*\}", raw_short)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, dict):
                return [data]
        except Exception:
            pass

    return []


def _page_no_from_image_name(img_file: str) -> int | None:
    """从图片文件名推导页码。

    支持：
    - page_12.png / page-12.jpg
    - 12.png
    - ..._p12.png
    """
    name = os.path.splitext(os.path.basename(img_file))[0]

    m = re.search(r"(?:^|[^0-9])(\d{1,5})$", name)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None

    m = re.search(r"page[_\-\s]*?(\d{1,5})", name, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None

    m = re.search(r"\bp(\d{1,5})\b", name, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None

    return None


def extract_folder_to_json_and_excel(
    img_dir: str,
    api_key: str = GLM_API_KEY,
    model: str = GLM_MODEL_VISION,
) -> Tuple[str, str]:
    if not os.path.isdir(img_dir):
        raise FileNotFoundError(img_dir)

    base_doc_name = _doc_name_from_folder(img_dir)
    img_files = _get_image_files(img_dir)

    client = ZhipuAiClient(api_key=api_key)

    all_data: List[Dict] = []
    for idx, img_file in enumerate(img_files, start=1):
        img_path = os.path.join(img_dir, img_file)
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 从文件名取页码（比模型输出更可靠）
        page_no = _page_no_from_image_name(img_file) or idx

        content = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
            {"type": "text", "text": _prompt(base_doc_name, img_file)},
        ]

        raw = ""
        retry_waits = [2, 4, 8, 16]
        for attempt in range(len(retry_waits) + 1):
            try:
                print(f"[extract] page {page_no}: stream start ({img_file})")
                stream_resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": content}],
                    # 关闭 thinking，避免 content 为空只给 reasoning_content，导致解析不到 JSON
                    thinking={"type": "disabled"},
                    stream=True,
                    max_tokens=6144,
                    temperature=0.2,
                    timeout=90,
                )
                raw_parts: List[str] = []
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
                                print(f"[extract] page {page_no}: streaming chars={streamed_chars}")
                                last_log_ts = now
                    except Exception:
                        continue
                raw = "".join(raw_parts)
                print(f"[extract] page {page_no}: stream done chars={len(raw)}")
                break
            except Exception as e:
                msg = str(e)
                if ("429" in msg or "APIReachLimitError" in msg) and attempt < len(retry_waits):
                    wait_s = retry_waits[attempt]
                    print(f"[extract] WARN: rate limited on {img_file}, retry in {wait_s}s")
                    time.sleep(wait_s)
                    continue
                print(f"[extract] WARN: extract failed on {img_file}: {e}")
                raw = ""
                break

        page_data = _extract_json_array(str(raw))
        for rec in page_data:
            if not isinstance(rec, dict):
                continue
            # 强制文件名=文档名
            rec["文件名"] = base_doc_name
            # 强制页码=从图片名推导的页码
            rec["页码"] = page_no
        all_data.extend(page_data)

    out_json = os.path.join(img_dir, "imgs_checklist.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    out_xlsx = os.path.join(img_dir, "imgs_checklist.xlsx")
    df = pd.DataFrame(all_data)
    df.to_excel(out_xlsx, index=False)

    return out_json, out_xlsx
