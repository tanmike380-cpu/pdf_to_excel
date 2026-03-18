# llm_config.py
# Centralized LLM wrapper using zai-sdk (ZhipuAiClient).
# Provides call_LLM(prompt) returning string output (non-streaming).

import os
import json
import concurrent.futures
from PIL import Image
import base64
import io
from typing import Any, Iterable, Optional

from config.settings import GLM_API_KEY, GLM_MODEL_VISION

# Deprecated: keep env override if user sets it, otherwise use settings
API_KEY = os.getenv("GLM_API_KEY", GLM_API_KEY)
MODEL_NAME = os.getenv("GLM_MODEL_VISION", GLM_MODEL_VISION)

try:
    import zai
    from zai import ZhipuAiClient
except Exception as e:
    raise SystemExit("缺少 zai-sdk，请运行: pip install zai-sdk\n错误: {}".format(e))


def get_client() -> ZhipuAiClient:
    return ZhipuAiClient(api_key=API_KEY)


client = get_client()


def call_LLM(prompt: str, stream: bool = False, images: Optional[list] = None, timeout: int = 60):
    """
    官方多模态API风格的LLM调用，支持图片（PIL.Image或路径）和文本混合。
    prompt: 文本内容
    images: PIL.Image对象或本地图片路径列表
    stream: 是否流式输出
    返回字符串或生成器
    """
    content = []
    if images:
        for im in images:
            if isinstance(im, str):
                with open(im, "rb") as img_file:
                    img_base = base64.b64encode(img_file.read()).decode("utf-8")
            else:
                buf = io.BytesIO()
                im.save(buf, format="PNG")
                img_base = base64.b64encode(buf.getvalue()).decode("utf-8")
            content.append(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base}"}}
            )
    content.append({"type": "text", "text": prompt})

    messages = [{"role": "user", "content": content}]
    try:
        resp: Any = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            thinking={"type": "enabled"},
            stream=stream,
            max_tokens=65536,
            temperature=1.0,
        )
        if stream:
            def stream_gen():
                for chunk in resp:  # type: ignore[operator]
                    try:
                        choices = getattr(chunk, "choices", None)
                        if not choices:
                            continue
                        delta = getattr(choices[0], "delta", None)
                        if delta is None:
                            continue
                        piece = getattr(delta, "content", None)
                        if piece:
                            yield str(piece)
                    except Exception:
                        continue
            return stream_gen()
        else:
            raw = ""
            try:
                choices = getattr(resp, "choices", None)
                if choices:
                    msg = choices[0].message
                    raw = getattr(msg, "content", "") or str(msg)
                else:
                    raw = str(resp)
            except Exception:
                raw = str(resp)
            return str(raw)
    except Exception as e:
        raise RuntimeError(f"调用模型失败: {e}")
