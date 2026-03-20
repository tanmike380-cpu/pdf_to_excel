#!/bin/bash

# PDF to Excel Web Application Startup Script

echo "=== Starting PDF to Excel Web Application ==="

# Check if GLM_API_KEY is set
if [ -z "$GLM_API_KEY" ]; then
    echo "ERROR: GLM_API_KEY environment variable is not set!"
    echo "Please set it first:"
    echo "  export GLM_API_KEY=your_api_key"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Start Backend
echo ""
echo "Starting Backend (FastAPI on port 8000)..."
cd "$SCRIPT_DIR/backend"
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start Frontend
echo ""
echo "Starting Frontend (Next.js on port 3000)..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Save PIDs
echo "$BACKEND_PID" > "$SCRIPT_DIR/.backend.pid"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/.frontend.pid"

echo ""
echo "=== Application Started ==="
echo "Backend API:  http://localhost:8000"
echo "Frontend UI:  http://localhost:3000"
echo "API Docs:     http://localhost:8000/docs"
echo ""
echo "To stop the application, run: ./stop.sh"
echo ""

# Wait for processes
wait
