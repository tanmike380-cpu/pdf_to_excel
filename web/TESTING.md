# PDF to Excel Web 应用 - 测试指南

## ✅ 服务状态

- **后端 API**: http://localhost:8000 ✓ 运行中
- **前端 UI**: http://localhost:3000 ✓ 运行中
- **API 文档**: http://localhost:8000/docs ✓ 可访问

## 🧪 测试步骤

### 方法 1: 使用 Web 界面（推荐）

1. 打开浏览器访问: **http://localhost:3000**
2. 点击 "Try Now" 或导航到 "Tool" 页面
3. 上传测试文件（例如桌面上的 PDF 文件）
4. 选择文档类型（如 "Invoice" 或 "Packing List"）
5. 点击 "Extract Data"
6. 查看预览结果
7. 下载 Excel 文件

### 方法 2: 使用 API 文档测试

1. 访问 API 文档: **http://localhost:8000/docs**
2. 找到 `/parse` 接口
3. 点击 "Try it out"
4. 上传文件并填写参数
5. 点击 "Execute"
6. 查看响应结果

## 📁 测试文件位置

你的桌面上有一些测试文件：

```
/Users/tankaixi/Desktop/招商青岛POC/
├── CV1000-01 CH 发运文件2nd.pdf
├── Case 案例/
│   ├── 82K DWT BC-20SCR通関文件.pdf
│   └── CV1000-01 CH cylinder DG 发票箱单.pdf
```

## 🎯 推荐测试用例

### 测试 1: 发票/装箱单提取
- 文件: `CV1000-01 CH cylinder DG 发票箱单.pdf`
- 文档类型: Invoice 或 Packing List
- 预期提取字段: PO号, 品名, 数量, 单位, 毛重, 净重

### 测试 2: 航运单据提取
- 文件: `CV1000-01 CH 发运文件2nd.pdf`
- 文档类型: Shipping Document
- 预期提取字段: PO号, 发货人, 品名, 数量

## 🔧 高级选项

### 自定义提取字段
在 "Target Columns" 输入框中填写（逗号分隔）：
```
文件名, 页码, PO号, 发货人, 品名, 数量, 单位, 毛重, 净重, HS编码
```

### 添加场景描述
在 "Scene Description" 输入框中填写：
```
这是招商工业港口物流单，内容多为船舶机电/消防系统/备件等术语
```

### 自定义翻译规则
在 "Translation Rules" 输入框中填写（每行一条）：
```
"PRESSURE GAUGE"="压力表"
"FIRE PUMP"="消防泵"
"VALVE"="阀门"
```

## ⚠️ 注意事项

1. **首次处理可能较慢**: PDF 转图片和 AI 提取需要时间
2. **文件大小限制**: 最大 20MB
3. **支持格式**: PDF, PNG, JPG, JPEG
4. **API Key 已设置**: ced7ab26819744958e9f6a49684e0a23.5RywtAIyVYS5EkRn

## 🐛 故障排查

### 如果前端无法访问
```bash
# 检查前端进程
ps aux | grep "next dev"

# 重启前端
cd /Users/tankaixi/.openclaw-autoclaw/workspace/pdf_to_excel/web/frontend
npm run dev
```

### 如果后端报错
```bash
# 检查后端进程
ps aux | grep uvicorn

# 重启后端
cd /Users/tankaixi/.openclaw-autoclaw/workspace/pdf_to_excel/web/backend
export GLM_API_KEY="ced7ab26819744958e9f6a49684e0a23.5RywtAIyVYS5EkRn"
export PYTHONPATH="/Users/tankaixi/.openclaw-autoclaw/workspace/pdf_to_excel:$PYTHONPATH"
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 API 端点

- `GET /health` - 健康检查
- `POST /parse` - 上传文件并提取数据
- `GET /download/{file_id}` - 下载生成的 Excel 文件

## 🎉 准备就绪！

打开浏览器访问 **http://localhost:3000** 开始测试吧！
