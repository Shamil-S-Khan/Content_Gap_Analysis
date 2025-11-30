@echo off
REM Quick start script for Windows - Content Gap Analysis API + Dashboard

echo ==========================================
echo Content Gap Analysis - Quick Start
echo ==========================================
echo.

echo Installing dependencies...
pip install -q -r requirements.txt

echo Downloading NLP models...
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

echo.
echo Starting services...
echo.
echo API Server: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo   - Health: http://localhost:8000/health
echo.
echo Dashboard: http://localhost:8050
echo.

REM Start API server in new window
start "Content Gap API" cmd /c "uvicorn api_server:app --host 0.0.0.0 --port 8000"

REM Wait a moment
timeout /t 3 /nobreak > nul

REM Start Dashboard in new window
start "Content Gap Dashboard" cmd /c "python dashboard_app.py"

echo.
echo ==========================================
echo Services started in separate windows!
echo ==========================================
echo.
echo Close the terminal windows to stop services
echo.

pause
