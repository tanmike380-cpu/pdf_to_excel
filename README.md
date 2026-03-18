# 招商青岛 POC（PDF/图片 → JSON → Excel → 术语标准化中文）

## 1. 项目目标

对一批报关/装箱/物流类 PDF（或已生成的图片页）进行自动化结构化抽取：

- 从每页图片抽取 **多行明细**（Packing List 一页多物料必须拆成多条记录）
- 规范字段（文件名=PDF名、页码来自图片名、PO号优先 Order No）
- 输出：
  - 英文原版 Excel：`<PDF名> checklist_EN.xlsx`
  - 中文标准化 Excel：`<PDF名> checklist.xlsx`（中文-only，结合术语词库 + LLM 补译）

---

## 2. 总体架构（Pipeline）

```text
┌────────────────────┐
│   输入：PDF 或 PDF目录  │
└─────────┬──────────┘
          │
          ▼
┌──────────────────────────────┐
│ Stage A: PDF → PNG（可跳过）   │
│ convert_png/pdf_to_png.py     │
└─────────┬────────────────────┘
          │  输出：<PDF名>Image/page_*.png
          ▼
┌──────────────────────────────┐
│ Stage B: PNG → JSON记录列表    │
│ src/pipeline/extract_images... │
│  - GLM-4.6V vision 抽取         │
│  - JSON 容错解析                │
│  - 强制覆盖 文件名/页码         │
└─────────┬────────────────────┘
          │ 输出：records(List[dict])
          │ 输出文件：<PDF名> checklist_EN.xlsx
          ▼
┌──────────────────────────────┐
│ Stage C: 术语词库加载/构建（一次）│
│ src/rag/build_vocab.py         │
│ src/rag/vocab_builder.py       │
└─────────┬────────────────────┘
          │ 输出：vocab_dict.json
          ▼
┌──────────────────────────────┐
│ Stage D: 英文 → 中文标准化翻译   │
│ src/rag/translate_json.py      │
│  - vocab命中直接替换成中文       │
│  - 其余走 GLM text 翻译补全      │
│  - 输出中文-only                 │
└─────────┬────────────────────┘
          │ 输出：<PDF名> checklist.xlsx
          ▼
┌────────────────────┐
│   最终交付：中英文Excel │
└────────────────────┘
```

---

## 3. 各阶段输入 / 输出定义

### Stage A：PDF → PNG（可跳过）

**负责文件**：`convert_png/pdf_to_png.py`

- 输入：
  - 单个 PDF：`xxx.pdf`
- 输出：
  - 图片目录：`xxxImage/`
  - 页图片：`xxxImage/page_1.png`, `page_2.png`, ...
- 规则：
  - 若 `xxxImage` 已存在则跳过（避免重复转图）

---

### Stage B：PNG → records(JSON list) → 英文Excel

**负责文件**：`src/pipeline/extract_images_to_json.py`

- 输入：
  - 图片目录：`<PDF名>Image/page_*.png`
  - doc_name（从图片目录名推导）
- LLM：
  - 模型：`GLM_MODEL_VISION`（多模态）
  - 关键设置：`thinking disabled`（避免只有 reasoning 导致 content 为空）
- 输出（内存结构）：
  - `records: List[dict]`
- 输出（文件）：
  - 英文原版 Excel：`<PDF名> checklist_EN.xlsx`（主流程中重命名得到）
- 抽取字段（每条记录一行）：
  - `文件名, 页码, PO号, 发货人, 品名, 数量, 单位, 毛重, 净重, HS编码, 总毛重, 备注, 验收`
- 强制规则（后处理覆盖）：
  - `文件名`：强制=图片目录推导的 PDF 名（不是图片名）
  - `页码`：强制从图片文件名推导（`page_17.png → 17`），不信模型
  - `PO号`：prompt 强调优先 `Order No/PO No`，`Contract No` 不算 PO
  - Packing List：一页多行物料必须拆成多条记录（list 多元素）

---

### Stage C：术语词库（RAG）加载 / 缺失才构建

**负责文件**：
- `src/rag/build_vocab.py`：`build_vocab_if_missing()`
- `src/rag/vocab_builder.py`：真正从词库 PDF 构建 `vocab_dict.json`

- 输入：
  - 术语 PDF（配置或参数传入）：`--rag-pdf`
- 输出：
  - `vocab_dict.json`（英文 → 中文映射，当前约 1179 条）
- 规则：
  - vocab json 存在就跳过构建
  - 主流程中 **只加载一次**，后续所有 PDF 复用，避免反复解析

---

### Stage D：records → 中文-only records → 中文Excel

**负责文件**：`src/rag/translate_json.py`

- 输入：
  - Stage B 的 records（英文/混合）
  - vocab dict（英文→中文）
- 输出：
  - 中文-only records（字段值尽量全中文）
  - `<PDF名> checklist.xlsx`
- 规则：
  - vocab 命中：直接替换为中文（不保留英文括号）
  - 未命中：分块调用 `GLM_MODEL_TEXT` 做补译
  - 禁止把 `reasoning_content` 混进结果（只取 `content`）

---

## 4. 目录/文件职责（关键入口）

- `main.py`
  - 全流程入口：PDF→图片→抽取→英文Excel→中文Excel
  - 参数：
    - `--pdf` 单个 PDF
    - `--pdf-dir` 目录递归批处理
    - `--rag-vocab` 指定 vocab json（可选）
    - `--rag-pdf` vocab 不存在时用来构建的 PDF（可选）
- `config/settings.py`
  - 集中配置：API KEY / 模型名 / vocab 路径等
- `debug_single_image_extract.py`
  - 单页调试：直接对某张 `page_*.png` 跑 vision 抽取 + JSON parse（用于定位 Packing List 长页场景）

---

## 5. 运行方式（全量）

`main.py` 必须传 `--pdf` 或 `--pdf-dir`。

- 跑单个 PDF：
  - `./.venv/bin/python -u main.py --pdf "/abs/path/xxx.pdf"`
- 跑一个目录下所有 PDF（递归）：
  - `./.venv/bin/python -u main.py --pdf-dir "/abs/path/包含多个PDF的目录"`

---

## 6. 已知注意点

- Python 3.14 可能出现依赖兼容警告（例如 pydantic v1 warning）。当前不影响主流程，但长期建议换 3.10/3.11。
- Packing List 长页稳定性关键点：
  - vision 抽取必须 `thinking disabled`
  - `max_tokens` 需要足够大
  - JSON 解析截取窗口需足够大（已为长页扩容）
