"""Algorithm adapter - wraps existing pdf_to_excel pipeline with custom config."""

import os
import sys
import json
import base64
import time
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# Add parent directories to path to import algorithm modules
ALGORITHM_ROOT = Path(__file__).parent.parent.parent.parent
if str(ALGORITHM_ROOT) not in sys.path:
    sys.path.insert(0, str(ALGORITHM_ROOT))

from zai import ZhipuAiClient

from app.schemas.response import StandardParseResult
from app.core.logger import get_logger

logger = get_logger("algorithm_adapter")

# Import algorithm components
try:
    from config.settings import GLM_API_KEY, GLM_MODEL_VISION, GLM_MODEL_TEXT, DOMAIN_CONTEXT, IMAGE_FOLDER_SUFFIX
    from convert_png.pdf_to_png import pdf_to_images_folder
    from vocab_mapper import load_vocab
except ImportError as e:
    logger.error(f"Failed to import algorithm modules: {e}")
    raise


def build_custom_extract_prompt(
    base_doc_name: str,
    target_columns: List[str] = None,
    document_type: str = "auto_detect",
    scene_description: str = "",
) -> str:
    """Build extraction prompt with custom columns and context."""
    
    # Default columns
    default_columns = ["文件名", "页码", "PO号", "发货人", "品名", "数量", "单位", "毛重", "净重", "HS编码", "总毛重", "备注", "验收"]
    columns = target_columns if target_columns else default_columns
    
    # Build example JSON
    example_fields = ", ".join([f'"{col}":""' for col in columns])
    example = f'[{{"文件名":"{base_doc_name}","页码":1,{example_fields}}}]'
    
    # Document type hint
    doc_type_hints = {
        "shipping_document": "这是一份航运/物流单据。",
        "invoice": "这是一份发票(Invoice)。",
        "packing_list": "这是一份装箱单(Packing List)，通常同一页会有多行品名/物料，请把每一行都输出为数组中的一条记录。",
        "bill_of_lading": "这是一份提单(Bill of Lading)。",
        "custom": "",
    }
    doc_hint = doc_type_hints.get(document_type, "")
    
    # Scene description
    scene = f"\n场景说明：{scene_description}" if scene_description else ""
    
    columns_str = "、".join(columns)
    
    prompt = (
        f"你现在看到的是一份文档扫描图片，来源文件名为：{base_doc_name}。"
        f"{doc_hint}"
        f"{scene}"
        f"\n请你识别图片中的主要字段，并输出结构化JSON数组。"
        f"\n需要抽取的字段（中文字段名）：{columns_str}"
        f"\n重要规则："
        f"\n- PO号请优先从单据中的 Order No / Order Number / PO No / Purchase Order No 提取；"
        f"\n- Contract No / Contract Number 不是 PO号；"
        f"\n- 如果是 Packing List 或类似清单页面，通常同一页会有多行品名/物料等信息：请把每一行都输出为数组中的一条记录；"
        f"\n- 注意列名对齐：有时候在list页中是 'No + 品名' 如: '28 PRESSURE GAUGE'，这时要把数字'28'去掉才能得到正确的品名；"
        f"\n- 只有当本页完全没有物料明细时，才输出空数组 []；"
        f"\n- 输出必须是严格JSON，不要输出任何解释、步骤、分析。"
        f"\n示例：{example}"
    )
    return prompt


def extract_json_array(raw: str) -> List[Dict]:
    """Extract JSON array from LLM response."""
    raw_short = (raw or "")[:50000]
    
    # Try to find array
    m = re.search(r"\[\s*\{[\s\S]*?\}\s*\]", raw_short)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]
        except Exception:
            pass
    
    # Try single object
    m = re.search(r"\{[\s\S]*\}", raw_short)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, dict):
                return [data]
        except Exception:
            pass
    
    return []


def page_no_from_image_name(img_file: str) -> Optional[int]:
    """Extract page number from image filename."""
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
    
    return None


def get_image_files(img_dir: str) -> List[str]:
    """Get sorted list of image files."""
    exts = {".png", ".jpg", ".jpeg", ".bmp"}
    files = [f for f in os.listdir(img_dir) if os.path.splitext(f)[1].lower() in exts]
    
    def _sort_key(name: str):
        stem = os.path.splitext(name)[0]
        m = re.search(r"(\d+)$", stem)
        if m:
            return (0, int(m.group(1)), name)
        return (1, 0, name)
    
    files.sort(key=_sort_key)
    return files


def doc_name_from_folder(img_dir: str) -> str:
    """Extract document name from image folder name."""
    base = os.path.basename(img_dir)
    return base.removesuffix("Image")


def extract_images_to_records(
    img_dir: str,
    target_columns: List[str] = None,
    document_type: str = "auto_detect",
    scene_description: str = "",
    api_key: str = GLM_API_KEY,
    model: str = GLM_MODEL_VISION,
) -> List[Dict]:
    """Extract records from images folder using GLM-4.6V."""
    
    base_doc_name = doc_name_from_folder(img_dir)
    img_files = get_image_files(img_dir)
    
    if not img_files:
        return []
    
    client = ZhipuAiClient(api_key=api_key)
    all_data: List[Dict] = []
    
    for idx, img_file in enumerate(img_files, start=1):
        img_path = os.path.join(img_dir, img_file)
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        page_no = page_no_from_image_name(img_file) or idx
        
        prompt = build_custom_extract_prompt(
            base_doc_name, target_columns, document_type, scene_description
        )
        
        content = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
            {"type": "text", "text": prompt},
        ]
        
        raw = ""
        retry_waits = [2, 4, 8, 16]
        for attempt in range(len(retry_waits) + 1):
            try:
                logger.info(f"Extracting page {page_no}: {img_file}")
                stream_resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": content}],
                    thinking={"type": "disabled"},
                    stream=True,
                    max_tokens=6144,
                    temperature=0.2,
                    timeout=90,
                )
                raw_parts: List[str] = []
                for chunk in stream_resp:
                    try:
                        choices = getattr(chunk, "choices", None)
                        if not choices:
                            continue
                        delta = getattr(choices[0], "delta", None)
                        piece = getattr(delta, "content", None) if delta is not None else None
                        if piece:
                            raw_parts.append(piece)
                    except Exception:
                        continue
                raw = "".join(raw_parts)
                logger.info(f"Page {page_no} extracted: {len(raw)} chars")
                break
            except Exception as e:
                msg = str(e)
                if ("429" in msg or "APIReachLimitError" in msg) and attempt < len(retry_waits):
                    wait_s = retry_waits[attempt]
                    logger.warning(f"Rate limited, retry in {wait_s}s")
                    time.sleep(wait_s)
                    continue
                logger.error(f"Extract failed on {img_file}: {e}")
                raw = ""
                break
        
        page_data = extract_json_array(str(raw))
        for rec in page_data:
            if not isinstance(rec, dict):
                continue
            rec["文件名"] = base_doc_name
            rec["页码"] = page_no
        all_data.extend(page_data)
    
    return all_data


def has_chinese(s: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def apply_vocab_zh_only(text: str, vocab: Dict[str, str]) -> str:
    """Replace English terms with Chinese from vocab."""
    if not text:
        return text
    items = sorted(vocab.items(), key=lambda kv: len(kv[0]), reverse=True)
    out = text
    for eng, zh in items:
        if not eng or not zh:
            continue
        pattern = re.compile(re.escape(eng), re.IGNORECASE)
        out = pattern.sub(lambda _m: zh, out)
    return out


def extract_english_chunks(text: str) -> List[str]:
    """Extract English text chunks from mixed text."""
    if not text:
        return []
    if not has_chinese(text):
        return [text]
    chunks = re.findall(r"[A-Za-z][A-Za-z0-9\-_/() ,.]*", text)
    seen = set()
    out = []
    for c in chunks:
        c = c.strip()
        if len(c) < 2 or c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def glm_translate(text: str, client: ZhipuAiClient, domain_context: str) -> str:
    """Translate text using GLM."""
    prompt = (
        f"{domain_context}\n"
        f"- 请将下面英文内容翻译成标准、专业的中文（偏船舶机电/消防/物流单语境）。"
        f"- 只返回中文翻译结果，不要解释。\n"
        f"英文：{text}"
    )
    
    retry_waits = [2, 4, 8]
    for attempt in range(len(retry_waits) + 1):
        try:
            stream_resp = client.chat.completions.create(
                model=GLM_MODEL_TEXT,
                messages=[{"role": "user", "content": prompt}],
                thinking={"type": "disabled"},
                stream=True,
                max_tokens=256,
                temperature=0.1,
                timeout=60,
            )
            out_parts: List[str] = []
            for chunk in stream_resp:
                try:
                    choices = getattr(chunk, "choices", None)
                    if not choices:
                        continue
                    delta = getattr(choices[0], "delta", None)
                    piece = getattr(delta, "content", None) if delta is not None else None
                    if piece:
                        out_parts.append(piece)
                except Exception:
                    continue
            resp = "".join(out_parts)
            return resp.strip().splitlines()[0].strip().strip('"').strip("'")
        except Exception as e:
            msg = str(e)
            if ("429" in msg or "APIReachLimitError" in msg) and attempt < len(retry_waits):
                time.sleep(retry_waits[attempt])
                continue
            logger.error(f"Translation failed: {e}")
            return ""
    return ""


def translate_records(
    records: List[Dict],
    vocab: Dict[str, str],
    translation_rules: Dict[str, str],
    scene_description: str = "",
    fields_to_translate: List[str] = None,
) -> List[Dict]:
    """Translate records using vocab and GLM."""
    if fields_to_translate is None:
        fields_to_translate = ["品名", "备注"]
    
    # Merge user rules into vocab (higher priority)
    merged_vocab = {**vocab, **translation_rules}
    
    client = ZhipuAiClient(api_key=GLM_API_KEY)
    domain_context = scene_description if scene_description else DOMAIN_CONTEXT
    
    for rec in records:
        if not isinstance(rec, dict):
            continue
        for field in fields_to_translate:
            val = rec.get(field)
            if isinstance(val, str) and val.strip():
                # Apply vocab
                out = apply_vocab_zh_only(val, merged_vocab)
                
                # If still has English, use GLM
                if re.search(r"[A-Za-z]", out):
                    for chunk in extract_english_chunks(out):
                        # Skip company names
                        upper = chunk.upper()
                        if any(x in upper for x in [" INC", " LTD", " LIMITED", " CO.", " COMPANY"]):
                            continue
                        zh = glm_translate(chunk, client, domain_context)
                        if zh:
                            out = out.replace(chunk, zh)
                rec[field] = out
    
    return records


def run_pipeline(
    file_path: str,
    document_type: str = "auto_detect",
    target_columns: List[str] = None,
    scene_description: str = "",
    translation_rules: Dict[str, str] = None,
    sheet_title: str = "Extraction Result",
    vocab_path: str = None,
) -> StandardParseResult:
    """
    Main pipeline entry point.
    
    Args:
        file_path: Path to input file (PDF or image)
        document_type: auto_detect, shipping_document, invoice, packing_list, bill_of_lading, custom
        target_columns: List of column names to extract
        scene_description: Domain context for extraction/translation
        translation_rules: Dict of English->Chinese translation rules
        sheet_title: Excel sheet title
        vocab_path: Path to vocab JSON file
    
    Returns:
        StandardParseResult with columns, rows, warnings, missing_fields
    """
    start_time = time.time()
    
    if translation_rules is None:
        translation_rules = {}
    
    logger.info(f"Pipeline started: file={file_path}, doc_type={document_type}")
    
    result = StandardParseResult()
    
    try:
        # Step 1: Convert PDF to images if needed
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            logger.info("Converting PDF to images...")
            img_dir = pdf_to_images_folder(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            # Create temp image dir with single image
            img_dir = os.path.dirname(file_path)
        elif ext == ".txt":
            # Text file - for now, skip (could be used for OCR results)
            logger.warning("Text file not directly supported for extraction")
            result.warnings.append("Text files are not supported for direct extraction")
            return result
        else:
            result.warnings.append(f"Unsupported file type: {ext}")
            return result
        
        # Step 2: Extract records from images
        logger.info(f"Extracting from images in: {img_dir}")
        records = extract_images_to_records(
            img_dir,
            target_columns=target_columns,
            document_type=document_type,
            scene_description=scene_description,
        )
        
        if not records:
            logger.warning("No records extracted")
            result.warnings.append("No records could be extracted from the document")
            return result
        
        logger.info(f"Extracted {len(records)} records")
        
        # Step 3: Load vocab
        vocab = {}
        if vocab_path and os.path.isfile(vocab_path):
            try:
                vocab = load_vocab(vocab_path)
                logger.info(f"Loaded vocab: {len(vocab)} entries")
            except Exception as e:
                logger.warning(f"Failed to load vocab: {e}")
        
        # Step 4: Translate records
        if translation_rules or vocab:
            logger.info("Translating records...")
            records = translate_records(
                records, vocab, translation_rules, scene_description
            )
        
        # Step 5: Determine columns
        if target_columns:
            result.columns = target_columns
        else:
            # Collect all unique keys from records
            all_keys = set()
            for rec in records:
                all_keys.update(rec.keys())
            # Put common fields first
            priority = ["文件名", "页码", "PO号", "发货人", "品名", "数量", "单位", "毛重", "净重", "HS编码", "总毛重", "备注", "验收"]
            result.columns = [k for k in priority if k in all_keys]
            result.columns.extend([k for k in sorted(all_keys) if k not in result.columns])
        
        # Step 6: Normalize rows
        for rec in records:
            row = {}
            for col in result.columns:
                row[col] = str(rec.get(col, ""))
            result.rows.append(row)
        
        # Step 7: Check missing fields
        if target_columns:
            for col in target_columns:
                found = any(rec.get(col, "").strip() for rec in records)
                if not found:
                    result.missing_fields.append(col)
        
        elapsed = time.time() - start_time
        logger.info(f"Pipeline completed: {len(result.rows)} rows, {elapsed:.2f}s")
        
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        result.warnings.append(f"Pipeline error: {str(e)}")
    
    return result
