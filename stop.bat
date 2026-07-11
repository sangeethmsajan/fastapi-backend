@echo off
echo Stopping IOSAF...

:: Stop ZAP daemon container
echo Stopping ZAP daemon...
docker stop zap-daemon
echo ZAP stopped

:: Kill FastAPI window
echo Stopping FastAPI...
taskkill /FI "WINDOWTITLE eq FastAPI Server" /F

:: Kill Celery window
echo Stopping Celery...
taskkill /FI "WINDOWTITLE eq Celery Worker" /F

echo.
echo ================================
echo All services stopped
echo ================================
pause