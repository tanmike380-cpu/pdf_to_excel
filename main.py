# -*- coding: utf-8 -*-
"""Main pipeline:
1) 将指定 PDF（或目录下全部 PDF）按页转图片（如已存在则跳过）
2) 用 GLM-4.6V 逐张图片抽取物流字段 -> 输出 imgs_checklist.json + imgs_checklist.xlsx
3) 基于术语库（RAG）先查表；未命中则结合“招商工业港口物流单”语境用 GLM 翻译 -> 输出 translated JSON/Excel

用法示例：
  python main.py --pdf "/path/to/xxx.pdf"
  python main.py --pdf-dir "/Users/tankaixi/Desktop/招商青岛POC" 
"""

import argparse
import os
from pathlib import Path

from config.settings import (
    RAG_PDF_PATH,
    VOCAB_JSON_PATH,
)
from convert_png.pdf_to_png import pdf_to_images_folder

from src.pipeline.extract_images_to_json import extract_folder_to_json_and_excel
from src.rag.build_vocab import build_vocab_if_missing
from src.rag.translate_json import translate_json_to_excel
from vocab_mapper import load_vocab


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=str, default=None, help="单个PDF路径")
    parser.add_argument("--pdf-dir", type=str, default=None, help="包含多个PDF的目录，递归扫描")
    parser.add_argument("--rag-pdf", type=str, default=RAG_PDF_PATH)
    parser.add_argument("--rag-vocab", type=str, default=VOCAB_JSON_PATH)
    args = parser.parse_args()

    # 0) 确保词库存在
    build_vocab_if_missing(rag_pdf=args.rag_pdf, vocab_json=args.rag_vocab)

    # 0.1) 词典只解析一次，后面全部复用（避免每个PDF都重复load，很慢）
    vocab = load_vocab(args.rag_vocab)
    print(f"[main] vocab loaded once: {args.rag_vocab} (size={len(vocab)})")

    pdf_paths = []
    if args.pdf:
        pdf_paths = [Path(args.pdf)]
    elif args.pdf_dir:
        root = Path(args.pdf_dir)
        pdf_paths = list(root.rglob("*.pdf"))
    else:
        raise SystemExit("请提供 --pdf 或 --pdf-dir")

    for pdf_path in pdf_paths:
        if not pdf_path.is_file():
            continue

        # 1) PDF -> images folder
        img_dir = pdf_to_images_folder(str(pdf_path))

        # 2) images -> json/xlsx
        out_json, out_xlsx = extract_folder_to_json_and_excel(img_dir)

        # 重命名原始英文版 Excel：<PDF名> checklist_EN.xlsx
        checklist_en_xlsx_name = f"{pdf_path.stem} checklist_EN.xlsx"
        checklist_en_xlsx_path = os.path.join(img_dir, checklist_en_xlsx_name)
        try:
            if os.path.abspath(out_xlsx) != os.path.abspath(checklist_en_xlsx_path):
                if os.path.exists(checklist_en_xlsx_path):
                    os.remove(checklist_en_xlsx_path)
                os.replace(out_xlsx, checklist_en_xlsx_path)
                out_xlsx = checklist_en_xlsx_path
        except Exception as e:
            print(f"[main] WARN: rename EN checklist failed: {e}")

        # 3) rag translate -> translated json/xlsx
        checklist_xlsx_name = f"{pdf_path.stem} checklist.xlsx"
        translate_json_to_excel(
            in_json=out_json,
            vocab_json=args.rag_vocab,
            out_json=os.path.join(img_dir, "imgs_checklist_translated.json"),
            out_xlsx=os.path.join(img_dir, checklist_xlsx_name),
            vocab=vocab,
        )

        print(
            f"DONE: {pdf_path.name}\n"
            f"  images: {img_dir}\n"
            f"  json: {out_json}\n"
            f"  checklist_en_xlsx: {out_xlsx}\n"
            f"  checklist_xlsx: {os.path.join(img_dir, checklist_xlsx_name)}"
        )


if __name__ == "__main__":
    main()
