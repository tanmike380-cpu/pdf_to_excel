# -*- coding: utf-8 -*-
"""PDF -> PNG (每页一张)。
输出目录：<PDF同目录>/<PDF名>Image
如果目录已存在且包含 page_*.png 则跳过。
"""

import os
from pathlib import Path

try:
    from pdf2image import convert_from_path
except ImportError:
    raise ImportError("pdf2image not installed. Run: pip install pdf2image")


def pdf_to_images_folder(pdf_file: str, dpi: int = 300, image_folder_suffix: str = "Image") -> str:
    """
    Convert PDF to images (one PNG per page).
    
    Args:
        pdf_file: Path to PDF file
        dpi: Resolution for conversion (default 300)
        image_folder_suffix: Suffix for output folder (default "Image")
    
    Returns:
        Path to output folder containing page_*.png files
    """
    pdf_path = Path(pdf_file)
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_file)

    out_dir = pdf_path.parent / f"{pdf_path.stem}{image_folder_suffix}"

    if out_dir.exists():
        existing = sorted(out_dir.glob("page_*.png"))
        if existing:
            return str(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    images = convert_from_path(str(pdf_path), dpi=dpi)
    for i, img in enumerate(images, start=1):
        img.save(out_dir / f"page_{i}.png", "PNG")

    return str(out_dir)
