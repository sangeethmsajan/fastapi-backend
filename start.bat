@echo off
echo Starting IOSAF...

:: Step 1 - Start ZAP daemon container
echo Starting ZAP daemon...
docker start zap-daemon
if %errorlevel% neq 0 (
    echo ZAP container not found, creating new one...
    docker run -d --name zap-daemon -p 8080:8080 ghcr.io/zaproxy/zaproxy:stable zap.sh -daemon -port 8080 -host 0.0.0.0 -config api.key=iosafkey -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true
)
echo Waiting for ZAP to start...
timeout /t 10 /nobreak > nul
echo ZAP daemon ready on port 8080

:: Step 2 - Start FastAPI
echo Starting FastAPI...
start "FastAPI Server" cmd /k ".venv\Scripts\activate && uvicorn app.main:app --reload"
timeout /t 2 /nobreak > nul

:: Step 3 - Start Celery
echo Starting Celery...
start "Celery Worker" cmd /k ".venv\Scripts\activate && celery -A app.celery_app worker --loglevel=info --pool=solo"

echo.
echo ================================
echo All services started
echo ZAP     = http://localhost:8080
echo FastAPI = http://localhost:8000
echo Celery  = see Celery window
echo ================================