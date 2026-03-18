# -*- coding: utf-8 -*-
"""调试：单张图片抽取（复用 src/pipeline/extract_images_to_json.py 的提示词与解析逻辑）。

用法：
  ./.venv/bin/python -u debug_single_image_extract.py \
    --image "/path/to/page_17.png" \
    --img-dir "/path/to/<doc>Image"

说明：
- 需要传 img-dir 用于推导“文件名”(doc name)。
- 输出打印模型原始返回片段，以及解析后的 JSON 结果。
"""

import argparse
import base64
import os

from zai import ZhipuAiClient

from config.settings import GLM_API_KEY, GLM_MODEL_VISION
from src.pipeline.extract_images_to_json import _doc_name_from_folder, _prompt, _extract_json_array, _page_no_from_image_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--img-dir", required=True, help="Image folder，用于推导文件名")
    args = parser.parse_args()

    img_path = args.image
    img_dir = args.img_dir

    base_doc_name = _doc_name_from_folder(img_dir)
    page_no = _page_no_from_image_name(os.path.basename(img_path))

    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    content = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
        {"type": "text", "text": _prompt(base_doc_name, os.path.basename(img_path))},
    ]

    client = ZhipuAiClient(api_key=GLM_API_KEY)
    resp = client.chat.completions.create(
        model=GLM_MODEL_VISION,
        messages=[{"role": "user", "content": content}],
        thinking={"type": "disabled"},
        stream=False,
        max_tokens=8192,
        temperature=0.2,
    )

    raw = ""
    try:
        choices = getattr(resp, "choices", None)
        if choices:
            msg = choices[0].message
            # 只取 content，避免 reasoning_content 混入导致无法解析 JSON
            raw = getattr(msg, "content", "") or ""
        else:
            raw = ""
    except Exception:
        raw = ""

    print("==== IMAGE ====")
    print(img_path)
    print("page_no_from_name:", page_no)
    print("==== RAW (head 3000) ====")
    print(str(raw)[:3000])
    print("==== PARSED ====")
    data = _extract_json_array(str(raw))
    for rec in data:
        if isinstance(rec, dict):
            rec["文件名"] = base_doc_name
            if page_no:
                rec["页码"] = page_no
    print(data)


if __name__ == "__main__":
    main()
