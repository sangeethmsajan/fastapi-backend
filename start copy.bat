@echo off
echo Starting IOSAF...

:: Start FastAPI in a new terminal window
start "FastAPI Server" cmd /k ".venv\Scripts\activate && uvicorn app.main:app --reload"

:: Wait 2 seconds so FastAPI starts first
timeout /t 2 /nobreak > nul

:: Start Celery in a new terminal window
start "Celery Worker" cmd /k ".venv\Scripts\activate && celery -A app.celery_app worker --loglevel=info --pool=solo"

echo Both services started.