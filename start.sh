#!/bin/bash
# Quick start script for Content Gap Analysis API + Dashboard

echo "=========================================="
echo "Content Gap Analysis - Quick Start"
echo "=========================================="
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running in Docker container"
else
    echo "Running locally"
    
    # Check Python
    if ! command -v python &> /dev/null; then
        echo "Error: Python not found"
        exit 1
    fi
    
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    # Download models
    echo "Downloading NLP models..."
    python -m spacy download en_core_web_sm -q
    python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)"
fi

echo ""
echo "Starting services..."
echo ""
echo "API Server: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "Dashboard: http://localhost:8050"
echo ""

# Start API in background
echo "Starting API server..."
uvicorn api_server:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait a moment
sleep 2

# Start Dashboard
echo "Starting Dashboard..."
python dashboard_app.py &
DASH_PID=$!

echo ""
echo "=========================================="
echo "Services running!"
echo "  API PID: $API_PID"
echo "  Dashboard PID: $DASH_PID"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for interruption
trap "echo 'Stopping services...'; kill $API_PID $DASH_PID; exit" INT TERM

# Keep script running
wait
