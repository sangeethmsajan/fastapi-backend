@echo off
echo Stopping IOSAF...
taskkill /FI "WINDOWTITLE eq FastAPI Server" /F
taskkill /FI "WINDOWTITLE eq Celery Worker" /F
echo Done.