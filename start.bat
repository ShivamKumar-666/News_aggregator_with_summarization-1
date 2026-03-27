@echo off
echo ===================================================
echo Starting AI News Aggregator Services
echo ===================================================

echo [1/3] Starting Backend API (Port 3000)...
start "Backend API" cmd /k "cd backend && npm start"

echo [2/3] Starting Frontend UI (Port 4200)...
start "Frontend UI" cmd /k "cd frontend && npm start"

echo [3/3] Starting AI Service (Port 5000)...
start "AI Service" cmd /k "cd ai-service && if not exist venv3 (python -m venv venv3 && .\venv3\Scripts\pip install python-dotenv langchain-text-splitters langchain-community langchain-huggingface chromadb groq newspaper3k requests flask flask-cors lxml_html_clean sentence-transformers) && .\venv3\Scripts\python app.py"

echo.
echo ===================================================
echo Launching complete! 3 new terminal windows should
echo appear for the backend, frontend, and AI service.
echo.
echo Backend:   http://localhost:3000
echo Frontend:  http://localhost:4200
echo AI API:    http://localhost:5000
echo ===================================================
echo Please do not close the new windows or the services will stop.
echo You can now open your browser to http://localhost:4200
echo.
pause
