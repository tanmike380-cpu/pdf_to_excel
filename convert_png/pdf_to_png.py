# -*- coding: utf-8 -*-
"""PDF -> PNG (每页一张)。
输出目录：<PDF同目录>/<PDF名>Image
如果目录已存在且包含 page_*.png 则跳过。
"""

from pathlib import Path

from pdf2image import convert_from_path

from config.settings import IMAGE_FOLDER_SUFFIX


def pdf_to_images_folder(pdf_file: str, dpi: int = 300) -> str:
    pdf_path = Path(pdf_file)
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_file)

    out_dir = pdf_path.parent / f"{pdf_path.stem}{IMAGE_FOLDER_SUFFIX}"

    if out_dir.exists():
        existing = sorted(out_dir.glob("page_*.png"))
        if existing:
            return str(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    images = convert_from_path(str(pdf_path), dpi=dpi)
    for i, img in enumerate(images, start=1):
        img.save(out_dir / f"page_{i}.png", "PNG")

    return str(out_dir)
