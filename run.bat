@echo off
echo ===================================================
echo Starting Offensive Automation Framework services...
echo ===================================================

:: Ensure we are in the correct directory
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment 'venv' not found.
    echo Please make sure the 'venv' directory exists in this folder.
    pause
    exit /b
)

:: Ensure Redis and MySQL are running
echo Make sure Redis and MySQL/MariaDB are started on your system before proceeding.
echo (e.g. via Docker Desktop, or local Windows services)
echo.

:: Start Uvicorn in a new window
echo Starting FastAPI (Uvicorn) server on http://localhost:8000 ...
start "FastAPI Server" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --port 8000"

:: Start Celery Worker in a new window
echo Starting Celery Worker (solo pool) ...
start "Celery Worker" cmd /k "call venv\Scripts\activate.bat && python -m celery -A app.celery_app worker --loglevel=info --pool=solo"

:: Start Flower in a new window
echo Starting Celery Flower Monitor on http://localhost:5555 ...
start "Celery Flower" cmd /k "call venv\Scripts\activate.bat && python -m celery -A app.celery_app flower --port=5555"

echo.
echo ===================================================
echo Services launched!
echo - FastAPI Web Server: http://localhost:8000
echo - Swagger API Documentation: http://localhost:8000/docs
echo - Flower Celery Monitor: http://localhost:5555
echo ===================================================
echo.
pause
