"""Vocabulary management service - build and manage terminology databases."""

import os
import sys
import json
import base64
import time
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from app.schemas.vocab import VocabEntry, VocabInfo, VocabDetail
from app.schemas.response import StandardParseResult
from app.core.logger import get_logger
from app.core.config import GLM_API_KEY, GLM_MODEL_VISION, GLM_MODEL_TEXT

logger = get_logger("vocab_service")

# Vocab storage directory
VOCAB_DIR = Path("/Users/tankaixi/.openclaw-autoclaw/workspace/pdf_to_excel/vocabs")
VOCAB_DIR.mkdir(parents=True, exist_ok=True)

# Lazy load convert_png module
_pdf_to_images_folder = None


def _get_pdf_converter():
    """Lazy load PDF converter to avoid startup issues."""
    global _pdf_to_images_folder
    if _pdf_to_images_folder is not None:
        return _pdf_to_images_folder
    
    try:
        # Add algorithm root to path
        algo_root = Path(__file__).parent.parent.parent.parent.parent
        if str(algo_root) not in sys.path:
            sys.path.insert(0, str(algo_root))
        
        from convert_png.pdf_to_png import pdf_to_images_folder
        _pdf_to_images_folder = pdf_to_images_folder
        logger.info("PDF converter loaded successfully")
        return _pdf_to_images_folder
    except Exception as e:
        logger.error(f"Failed to load PDF converter: {e}")
        return None


class VocabService:
    """Service for managing terminology databases."""
    
    def __init__(self):
        self.vocab_dir = VOCAB_DIR
    
    def list_vocabs(self) -> List[VocabInfo]:
        """List all available vocabularies."""
        vocabs = []
        for f in self.vocab_dir.glob("*.json"):
            if f.stem == "vocab_dict":  # Skip legacy vocab_dict.json
                continue
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                info = VocabInfo(
                    id=f.stem,
                    name=data.get("name", f.stem),
                    description=data.get("description", ""),
                    entry_count=len(data.get("entries", [])),
                    created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
                    file_name=data.get("file_name", ""),
                )
                vocabs.append(info)
            except Exception as e:
                logger.warning(f"Failed to load vocab {f}: {e}")
        
        # Sort by created_at descending
        vocabs.sort(key=lambda v: v.created_at, reverse=True)
        return vocabs
    
    def get_vocab(self, vocab_id: str) -> Optional[VocabDetail]:
        """Get vocabulary details by ID."""
        vocab_file = self.vocab_dir / f"{vocab_id}.json"
        if not vocab_file.exists():
            return None
        
        try:
            with open(vocab_file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            
            entries = [
                VocabEntry(
                    english=e.get("english", ""),
                    chinese=e.get("chinese", ""),
                    source=e.get("source", ""),
                )
                for e in data.get("entries", [])
            ]
            
            return VocabDetail(
                id=vocab_id,
                name=data.get("name", vocab_id),
                description=data.get("description", ""),
                entry_count=len(entries),
                created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
                file_name=data.get("file_name", ""),
                entries=entries,
            )
        except Exception as e:
            logger.error(f"Failed to load vocab {vocab_id}: {e}")
            return None
    
    def get_vocab_dict(self, vocab_id: str) -> Dict[str, str]:
        """Get vocabulary as a simple dict (english -> chinese)."""
        vocab = self.get_vocab(vocab_id)
        if not vocab:
            return {}
        return {e.english: e.chinese for e in vocab.entries if e.english and e.chinese}
    
    def delete_vocab(self, vocab_id: str) -> bool:
        """Delete a vocabulary."""
        vocab_file = self.vocab_dir / f"{vocab_id}.json"
        if vocab_file.exists():
            vocab_file.unlink()
            return True
        return False
    
    def build_vocab_from_file(
        self,
        file_path: str,
        name: str,
        description: str,
        extraction_prompt: str,
        file_name: str = "",
    ) -> tuple[str, List[VocabEntry]]:
        """
        Build vocabulary from a dictionary file using VLM.
        """
        logger.info(f"Building vocab from: {file_path}")
        
        # Convert PDF to images if needed
        ext = os.path.splitext(file_path)[1].lower()
        img_dir = file_path
        
        if ext == ".pdf":
            pdf_converter = _get_pdf_converter()
            if pdf_converter:
                try:
                    img_dir = pdf_converter(file_path)
                    logger.info(f"PDF converted to images: {img_dir}")
                except Exception as e:
                    logger.error(f"PDF conversion failed: {e}")
                    return "", []
            else:
                logger.error("PDF converter not available")
                return "", []
        
        # Extract terminology from images
        entries = self._extract_terminology_from_images(
            img_dir=img_dir,
            extraction_prompt=extraction_prompt,
        )
        
        if not entries:
            logger.warning("No terminology entries extracted")
            return "", []
        
        # Save vocabulary
        vocab_id = f"vocab_{int(time.time() * 1000)}"
        vocab_file = self.vocab_dir / f"{vocab_id}.json"
        
        vocab_data = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "file_name": file_name,
            "entries": [
                {"english": e.english, "chinese": e.chinese, "source": e.source}
                for e in entries
            ],
        }
        
        with open(vocab_file, "w", encoding="utf-8") as fp:
            json.dump(vocab_data, fp, ensure_ascii=False, indent=2)
        
        logger.info(f"Vocab saved: {vocab_id}, {len(entries)} entries")
        return vocab_id, entries
    
    def _extract_terminology_from_images(
        self,
        img_dir: str,
        extraction_prompt: str,
    ) -> List[VocabEntry]:
        """Extract terminology pairs from images using VLM."""
        
        # Get image files
        img_files = self._get_image_files(img_dir)
        if not img_files:
            logger.warning(f"No images found in: {img_dir}")
            return []
        
        # Import ZhipuAiClient
        try:
            from zai import ZhipuAiClient
        except ImportError:
            logger.error("ZhipuAiClient not available")
            return []
        
        client = ZhipuAiClient(api_key=GLM_API_KEY)
        all_entries: List[VocabEntry] = []
        
        for idx, img_file in enumerate(img_files, start=1):
            img_path = os.path.join(img_dir, img_file)
            
            try:
                with open(img_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")
                
                # Build prompt for terminology extraction
                prompt = self._build_extraction_prompt(extraction_prompt, page_no=idx)
                
                content = [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    {"type": "text", "text": prompt},
                ]
                
                logger.info(f"Extracting terminology from page {idx}: {img_file}")
                
                # Call VLM
                raw = self._call_vlm(client, content)
                
                if raw:
                    entries = self._parse_terminology_response(raw, source=f"page_{idx}")
                    all_entries.extend(entries)
                    logger.info(f"Page {idx}: extracted {len(entries)} entries")
                
            except Exception as e:
                logger.error(f"Failed to process {img_file}: {e}")
                continue
        
        # Deduplicate by english term
        seen = set()
        unique_entries = []
        for e in all_entries:
            key = e.english.lower().strip()
            if key not in seen and e.english and e.chinese:
                seen.add(key)
                unique_entries.append(e)
        
        logger.info(f"Total unique entries: {len(unique_entries)}")
        return unique_entries
    
    def _build_extraction_prompt(self, user_prompt: str, page_no: int) -> str:
        """Build the full extraction prompt."""
        return f"""你是一个专业的术语词典抽取助手。

用户任务描述：
{user_prompt}

请从这张词典页面中抽取所有的英文术语和对应的中文翻译。

输出格式要求（严格JSON数组）：
```json
[
  {{"english": "PRESSURE GAUGE", "chinese": "压力表"}},
  {{"english": "FIRE PUMP", "chinese": "消防泵"}}
]
```

重要规则：
1. 每个条目必须包含 english 和 chinese 两个字段
2. english 是英文术语原文，保持原有大小写
3. chinese 是中文翻译
4. 如果页面没有术语对，输出空数组 []
5. 只输出JSON数组，不要有任何其他文字说明

第 {page_no} 页，请开始抽取："""
    
    def _call_vlm(self, client, content: list) -> str:
        """Call VLM with retry logic."""
        retry_waits = [2, 4, 8, 16]
        
        for attempt in range(len(retry_waits) + 1):
            try:
                stream_resp = client.chat.completions.create(
                    model=GLM_MODEL_VISION,
                    messages=[{"role": "user", "content": content}],
                    thinking={"type": "disabled"},
                    stream=True,
                    max_tokens=4096,
                    temperature=0.1,
                    timeout=90,
                )
                
                raw_parts = []
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
                
                return "".join(raw_parts)
                
            except Exception as e:
                msg = str(e)
                if ("429" in msg or "APIReachLimitError" in msg) and attempt < len(retry_waits):
                    logger.warning(f"Rate limited, retry in {retry_waits[attempt]}s")
                    time.sleep(retry_waits[attempt])
                    continue
                logger.error(f"VLM call failed: {e}")
                return ""
        
        return ""
    
    def _parse_terminology_response(self, raw: str, source: str = "") -> List[VocabEntry]:
        """Parse VLM response to extract terminology entries."""
        entries = []
        
        # Try to find JSON array
        m = re.search(r"\[\s*\{[\s\S]*?\}\s*\]", raw)
        if not m:
            return []
        
        try:
            data = json.loads(m.group(0))
            if not isinstance(data, list):
                return []
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                english = item.get("english", "").strip()
                chinese = item.get("chinese", "").strip()
                
                if english and chinese:
                    entries.append(VocabEntry(
                        english=english,
                        chinese=chinese,
                        source=source,
                    ))
        
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
        
        return entries
    
    def _get_image_files(self, img_dir: str) -> List[str]:
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


# Singleton instance
vocab_service = VocabService()
