# -*- coding: utf-8 -*-
"""对抽取结果 JSON 做 RAG 术语增强 + GLM 补译，然后转 Excel。"""

import json
import os
import re
import time
from typing import Dict, List, Optional

import pandas as pd
from zai import ZhipuAiClient

from config.settings import DOMAIN_CONTEXT, GLM_API_KEY, GLM_MODEL_TEXT
from Prompt.prompts import rag_translate_prompt
from vocab_mapper import load_vocab

FIELDS_TO_TRANSLATE = ["品名", "备注"]

# 强制补译的典型术语（库里缺失时确保翻译）
FORCE_GLM_TERMS = [
    "CO2 FIRE EXTINGUISHING SYSTEM",
]


def has_chinese(s: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def apply_vocab_zh_only(text: str, vocab: Dict[str, str]) -> str:
    """把命中的英文术语直接替换为中文（不保留英文）。大小写不敏感、长词优先。"""
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
    if not text:
        return []
    if not has_chinese(text):
        return [text]
    chunks = re.findall(r"[A-Za-z][A-Za-z0-9\-_/() ,.]*", text)
    seen = set()
    out = []
    for c in chunks:
        c = c.strip()
        if len(c) < 2:
            continue
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def glm_translate(text: str, client: ZhipuAiClient) -> str:
    prompt = rag_translate_prompt(DOMAIN_CONTEXT, text)
    resp = None
    retry_waits = [2, 4, 8, 16]
    for attempt in range(len(retry_waits) + 1):
        try:
            print(f"[translate_json] stream start: {text[:60]}")
            stream_resp = client.chat.completions.create(
                model=GLM_MODEL_TEXT,
                messages=[{"role": "user", "content": prompt}],
                # 关闭 thinking，减少返回结构/元信息干扰
                thinking={"type": "disabled"},
                stream=True,
                max_tokens=256,
                temperature=0.1,
                timeout=180,
            )
            out_parts: List[str] = []
            print("[translate_json] stream content: ", end="", flush=True)
            for chunk in stream_resp:
                try:
                    choices = getattr(chunk, "choices", None)
                    if not choices:
                        continue
                    delta = getattr(choices[0], "delta", None)
                    piece = getattr(delta, "content", None) if delta is not None else None
                    if piece:
                        out_parts.append(piece)
                        print(piece, end="", flush=True)
                except Exception:
                    continue
            print("")
            resp = "".join(out_parts)
            break
        except Exception as e:
            msg = str(e)
            # 高频 429：指数退避重试，避免整批任务直接中断
            if ("429" in msg or "APIReachLimitError" in msg) and attempt < len(retry_waits):
                wait_s = retry_waits[attempt]
                print(f"[translate_json] WARN: rate limited, retry in {wait_s}s")
                time.sleep(wait_s)
                continue
            print(f"[translate_json] WARN: glm_translate failed: {e}")
            return ""

    if resp is None:
        return ""

    # resp 是流式拼接后的文本
    try:
        out = str(resp).strip()

        # 防御：如果 SDK repr 泄漏进来，直接丢弃
        if "CompletionMessage" in out or "reasoning_content" in out:
            return ""

        # 再防御：如果模型违规输出“解释/步骤”，做一次简单截断（取第一行/去引号）
        out = out.splitlines()[0].strip().strip('"').strip("'")
        return out
    except Exception:
        return ""


def translate_text(text: str, vocab: Dict[str, str], client: ZhipuAiClient) -> str:
    """最终输出要求：只要中文。

    策略：
    1) 优先用 vocab 做英文->中文替换（中文-only）
    2) 若仍存在英文片段，再用 GLM 补翻译并替换为中文
    """
    if not text:
        return text

    # 先用词库做“中文替换”（最终只要中文）
    out = apply_vocab_zh_only(text, vocab)

    # 如果已经没有英文了，直接返回（避免多余调用）
    if not re.search(r"[A-Za-z]", out):
        return out

    # 词库缺项时强制补译：如果出现 term，就替换成 zh（不保留英文）
    for term in FORCE_GLM_TERMS:
        if re.search(re.escape(term), out, re.IGNORECASE):
            zh = glm_translate(term, client)
            if zh:
                out = re.sub(re.escape(term), zh, out, flags=re.IGNORECASE)

    # 剩余英文片段用 GLM 翻成中文，并替换为中文
    for chunk in extract_english_chunks(out):
        # 过滤明显是公司抬头的片段
        upper = chunk.upper()
        if any(x in upper for x in [" INC", " LTD", " LIMITED", " CO.", " COMPANY"]):
            continue

        zh = glm_translate(chunk, client)
        if not zh:
            continue

        # 只替换这一段英文为中文（不拼接英文）
        out = out.replace(chunk, zh)

    # 最后兜底：如果还残留大段英文，不再追加任何解释/对象repr
    return out


# 进程内缓存：避免每次 translate 都重新解析大词典
_VOCAB_CACHE: Dict[str, Dict[str, str]] = {}


def get_vocab_cached(vocab_json: str) -> Dict[str, str]:
    """缓存加载词典：同一个 vocab_json 在同一进程内只 load 一次。"""
    if vocab_json in _VOCAB_CACHE:
        return _VOCAB_CACHE[vocab_json]
    vocab = load_vocab(vocab_json)
    _VOCAB_CACHE[vocab_json] = vocab
    print(f"[translate_json] vocab loaded and cached: {vocab_json} (size={len(vocab)})")
    return vocab


def translate_json_to_excel(
    in_json: str,
    vocab_json: str,
    out_json: str,
    out_xlsx: str,
    vocab: Optional[Dict[str, str]] = None,
):
    if not os.path.isfile(in_json):
        raise FileNotFoundError(in_json)

    # 允许外部传入已加载的 vocab，避免重复解析
    if vocab is None:
        vocab = get_vocab_cached(vocab_json)
    else:
        print(f"[translate_json] vocab provided by caller (size={len(vocab)})")

    client = ZhipuAiClient(api_key=GLM_API_KEY)

    with open(in_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("输入JSON期望为数组(list)")

    for rec in data:
        if not isinstance(rec, dict):
            continue
        for field in FIELDS_TO_TRANSLATE:
            val = rec.get(field)
            if isinstance(val, str) and val.strip():
                rec[field] = translate_text(val, vocab, client)

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    df = pd.DataFrame(data)
    df.to_excel(out_xlsx, index=False)
