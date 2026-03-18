# -*- coding: utf-8 -*-
"""Centralized prompt templates for the project."""


# Used by: src/pipeline/extract_images_to_json.py 图片抽取prompt
def checklist_extract_prompt(base_doc_name: str) -> str:
    example = (
        "[{\"文件名\":\"" + base_doc_name + "\",\"页码\":1,\"PO号\":\"\",\"发货人\":\"\","
        "\"品名\":\"\",\"数量\":\"\",\"单位\":\"\",\"毛重\":\"\",\"净重\":\"\","
        "\"HS编码\":\"\",\"总毛重\":\"\",\"备注\":\"\",\"验收\":\"\"}]"
    )
    return (
        f"你现在看到的是一份物流清单/装箱单(Packing List)/发票的扫描图片，来源文件名为：{base_doc_name}。"
        "请你识别图片中的主要字段，并输出结构化JSON数组。\n"
        "字段要求（中文字段名）：文件名, 页码, PO号, 发货人, 品名, 数量, 单位, 毛重, 净重, HS编码, 总毛重, 备注, 验收。\n"
        "重要规则：\n"
        "- PO号请优先从单据中的 Order No / Order Number / PO No / Purchase Order No 提取；\n"
        "- Contract No / Contract Number 不是 PO号, 除非页面完全无法找到 Order No / Order Number / PO No / Purchase Order No。\n"
        "- 如果是 Packing List 页面，通常同一页会有多行品名/物料等信息：请把每一行都输出为数组中的一条记录（不要只挑一条，也不要跳过整页）。\n"
        "- ***注意列名对齐***: 有时候在list页中是 “No + 品名” 如: '28 PRESSURE GAUGE'这时你要去看'28'这个列的列名是否为'NO'，如果是这种情况则要把数字'28'去掉才能得到正确的品名。\n"
        "- 只有当本页完全没有物料明细时，才输出空数组 []。\n"
        "- 输出必须是严格JSON，*不要输出任何解释、步骤、分析*，你的任务就是抽取信息。\n"
        f"示例：{example}"
    )


# Used by: src/rag/translate_json.py 翻译prompt
def rag_translate_prompt(domain_context: str, text: str) -> str:
    return (
        f"{domain_context}\n"
        "- 请将下面英文内容翻译成标准、专业的中文（偏船舶机电/消防/物流单语境）优先从词库中查找。"
        "- 有些术语如果词库里没有，请你尽量根据我们这个场景的背景和上下文翻译准确（而不是直译）。\n"
        "- 有些品名只是case ID 或者 产品型号 如 's1','s2', 'Y18SCR-(A)L' 等这部分可以保留原样，不用翻译。\n"
        "- 只返回中文翻译结果，不要解释、不要输出任何额外字段。\n"
        f"英文：{text}"
    )


# Used by: src/rag/vocab_builder.py 词库抽取prompt
def vocab_builder_image_prompt(page_no: int) -> str:
    return (
        "你现在看到的是一本船舶机电英语手册的词汇/短句对照页截图。"
        "通常前几页是目录页，没有词汇对照，中间有些是标题，也没有对照。"
        "请仅基于图片内容抽取英文术语/英文短句与对应中文翻译，输出为英文到中文映射。"
        "词汇部分是先中文后英文的对照，短句部分是先英文后中文的对照。"
        "同一页可能出现词汇和短句部分，请你自行对齐配对。"
        "仅输出严格 JSON 对象，格式为 {\"English term\":\"中文翻译\", ...}。"
        "要求："
        "1) key 必须是英文；value 必须是中文；"
        "2) 不要输出解释、注释、markdown、代码块标记；"
        "3) 若该页是目录/标题页或无可配对术语，输出 {}。"
        f"（当前页码: {page_no}）"
    )
