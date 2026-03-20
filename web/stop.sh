#!/bin/bash

echo "=== Stopping PDF to Excel Web Application ==="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Kill Backend
if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/.backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID"
        echo "Backend stopped (PID: $BACKEND_PID)"
    fi
    rm "$SCRIPT_DIR/.backend.pid"
fi

# Kill Frontend
if [ -f "$SCRIPT_DIR/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/.frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID"
        echo "Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm "$SCRIPT_DIR/.frontend.pid"
fi

echo "Application stopped"
