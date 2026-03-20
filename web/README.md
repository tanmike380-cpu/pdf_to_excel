# PDF to Excel Web Application

Web interface for extracting structured data from PDFs and images using AI.

## Quick Start

### 1. Prerequisites

- Python 3.10+ (tested with 3.14)
- Node.js 18+
- GLM API Key (from ZhipuAI)

### 2. Setup

```bash
# Set your GLM API key
export GLM_API_KEY=your_api_key_here

# Install dependencies (first time only)
cd web/backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd ../frontend
npm install
```

### 3. Run

```bash
# From web directory
cd web
./start.sh
```

Or start manually:

```bash
# Terminal 1: Backend
cd web/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd web/frontend
npm run dev
```

### 4. Access

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features

### Supported File Types
- PDF documents
- Images: PNG, JPG, JPEG

### Document Types
- Auto Detect
- Shipping Document
- Invoice
- Packing List
- Bill of Lading
- Custom

### Extraction Options

1. **Target Columns**: Define custom fields to extract (comma-separated)
   - Example: `文件名, 页码, PO号, 品名, 数量, 单位`
   
2. **Scene Description**: Provide domain context for better accuracy
   - Example: `这是招商工业港口物流单，内容多为船舶机电/消防系统/备件等术语`

3. **Translation Rules**: Custom English-to-Chinese translation
   - Format: `"English Term"="中文翻译"` (one per line)
   - Example:
     ```
     "PRESSURE GAUGE"="压力表"
     "FIRE PUMP"="消防泵"
     ```

## Architecture

```
Frontend (Next.js + TypeScript + Tailwind)
    ↓ HTTP POST /parse
Backend (FastAPI + Python)
    ↓
Algorithm Pipeline
    ├─ PDF → Images (pdf2image)
    ├─ Vision Extraction (GLM-4.6V)
    ├─ Translation (GLM-5 + Vocab)
    └─ Excel Export (openpyxl)
```

## Environment Variables

### Backend
- `GLM_API_KEY`: Your GLM API key (required)
- `VOCAB_JSON_PATH`: Path to vocabulary JSON (optional)

### Frontend
- `NEXT_PUBLIC_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Troubleshooting

### Backend won't start
- Check if `GLM_API_KEY` is set: `echo $GLM_API_KEY`
- Check if port 8000 is free: `lsof -i :8000`

### Frontend won't start
- Check if port 3000 is free: `lsof -i :3000`
- Try deleting `node_modules` and reinstalling: `rm -rf node_modules && npm install`

### File upload fails
- Max file size: 20MB
- Supported formats: PDF, PNG, JPG, JPEG

### Extraction returns no results
- Try different document type
- Add scene description for domain context
- Check if the document contains extractable structured data

## Development

### Project Structure
```
web/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── services/     # Business logic
│   │   ├── schemas/      # Pydantic models
│   │   └── utils/        # Utilities
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   ├── lib/              # Utilities
│   └── types/            # TypeScript types
├── start.sh              # Start script
└── stop.sh               # Stop script
```

### Adding New Features

1. **New extraction field**: Update prompt in `backend/app/services/algorithm_adapter.py`
2. **New document type**: Add to `DocumentTypeSelect` component and routing logic
3. **Custom validation**: Update `frontend/lib/validators.ts`

## License

MIT
