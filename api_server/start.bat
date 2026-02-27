@echo off
REM Quick start script for self-hosted API (Windows)

echo Starting Callout Self-Hosted API...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed. Please install Docker Desktop first.
    echo Visit: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Start services
echo Starting Docker containers...
docker-compose up -d

REM Wait for services to be ready
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Check if services are running
docker ps | findstr callout-ollama >nul
if errorlevel 1 (
    echo Ollama service failed to start
    pause
    exit /b 1
) else (
    echo Ollama service is running
)

docker ps | findstr callout-api >nul
if errorlevel 1 (
    echo API service failed to start
    pause
    exit /b 1
) else (
    echo API service is running
)

REM Pull LLM model
echo.
echo Checking for LLM model...
docker exec callout-ollama ollama list | findstr "llama3.2:3b" >nul
if errorlevel 1 (
    echo Downloading llama3.2:3b model (this may take a few minutes)...
    docker exec callout-ollama ollama pull llama3.2:3b
    echo Model downloaded successfully
) else (
    echo Model llama3.2:3b already downloaded
)

REM Test API health
echo.
echo Testing API health...
timeout /t 2 /nobreak >nul
curl -s http://localhost:8000/health | findstr "healthy" >nul
if errorlevel 1 (
    echo API health check failed. Check logs with: docker-compose logs api
) else (
    echo API is healthy and ready!
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo    1. Update your .env file:
echo       USE_SELF_HOSTED_API=true
echo       SELF_HOSTED_API_URL=http://localhost:8000
echo.
echo    2. Run Callout:
echo       cd ..
echo       streamlit run app.py
echo.
echo Useful commands:
echo    - View logs: docker-compose logs -f
echo    - Stop services: docker-compose down
echo    - Restart services: docker-compose restart
echo.
pause
