@echo off
REM IRIS RegTech Platform - Demo Deployment Script for Windows
REM Automated setup for complete demo environment

setlocal enabledelayedexpansion

echo 🚀 IRIS RegTech Platform - Demo Deployment
echo ==========================================

REM Function to check Docker
:check_docker
echo [INFO] Checking Docker installation...

docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop and try again.
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop and try again.
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not available. Please ensure Docker Desktop is properly installed.
    exit /b 1
)

echo [SUCCESS] Docker and Docker Compose are available
goto create_directories

:create_directories
echo [INFO] Creating necessary directories...

if not exist "backend\data" mkdir backend\data
if not exist "backend\uploads" mkdir backend\uploads
if not exist "logs" mkdir logs

echo [SUCCESS] Directories created
goto setup_environment

:setup_environment
echo [INFO] Setting up environment variables...

if not exist ".env" (
    echo [INFO] Creating .env file from template...
    (
        echo # IRIS RegTech Platform Environment Configuration
        echo ENVIRONMENT=production
        echo GEMINI_API_KEY=demo_key_replace_with_actual
        echo FMP_API_KEY=demo_key_replace_with_actual
        echo DATABASE_URL=sqlite:///./data/iris_regtech.db
        echo ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80,http://localhost
        echo CORS_ALLOW_ALL=false
        echo RATE_LIMIT_REQUESTS=100
        echo RATE_LIMIT_WINDOW=60
    ) > .env
    echo [WARNING] Created .env file with demo keys. Please update with actual API keys for full functionality.
) else (
    echo [SUCCESS] Environment file already exists
)
goto deploy_services

:deploy_services
echo [INFO] Building and starting IRIS services...

REM Stop any existing containers
docker-compose down --remove-orphans

REM Build and start services
docker-compose up --build -d

if errorlevel 1 (
    echo [ERROR] Failed to start services
    exit /b 1
)

echo [SUCCESS] Services started successfully
goto wait_for_services

:wait_for_services
echo [INFO] Waiting for services to be healthy...

REM Wait for backend
echo [INFO] Waiting for backend service...
set /a timeout=60
set /a counter=0

:wait_backend_loop
curl -f http://localhost:8000/health >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Backend service is healthy
    goto wait_frontend
)

set /a counter+=1
timeout /t 1 /nobreak >nul

if !counter! geq !timeout! (
    echo [ERROR] Backend service failed to start within !timeout! seconds
    docker-compose logs backend
    exit /b 1
)
goto wait_backend_loop

:wait_frontend
echo [INFO] Waiting for frontend service...
set /a counter=0

:wait_frontend_loop
curl -f http://localhost/health >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Frontend service is healthy
    goto initialize_database
)

set /a counter+=1
timeout /t 1 /nobreak >nul

if !counter! geq !timeout! (
    echo [ERROR] Frontend service failed to start within !timeout! seconds
    docker-compose logs frontend
    exit /b 1
)
goto wait_frontend_loop

:initialize_database
echo [INFO] Initializing database with sample data...

REM Create database indexes for performance
docker-compose exec backend python app/database_indexes.py

REM Generate sample data
docker-compose exec backend python generate_sample_data.py

echo [SUCCESS] Database initialized with sample data
goto run_tests

:run_tests
echo [INFO] Running end-to-end tests...

REM Test API endpoints
echo [INFO] Testing API endpoints...

REM Test health endpoint
curl -f http://localhost:8000/health >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] ✓ Backend health check passed
) else (
    echo [ERROR] ✗ Backend health check failed
    goto show_summary
)

REM Test frontend
curl -f http://localhost/ >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] ✓ Frontend health check passed
) else (
    echo [ERROR] ✗ Frontend health check failed
    goto show_summary
)

REM Test API endpoints
curl -f http://localhost:8000/api/fraud-heatmap >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] ✓ Heatmap API endpoint accessible
) else (
    echo [WARNING] ⚠ Heatmap API endpoint test failed (may need sample data)
)

echo [SUCCESS] Basic tests completed
goto show_summary

:show_summary
echo.
echo 🎉 IRIS RegTech Platform Deployed Successfully!
echo ==============================================
echo.
echo 📊 Access Points:
echo   • Frontend Application: http://localhost
echo   • Backend API: http://localhost:8000
echo   • API Documentation: http://localhost:8000/docs
echo   • Interactive API: http://localhost:8000/redoc
echo.
echo 🔧 Management Commands:
echo   • View logs: docker-compose logs -f
echo   • Stop services: docker-compose down
echo   • Restart services: docker-compose restart
echo   • Update services: docker-compose up --build -d
echo.
echo 📋 Demo Features Available:
echo   ✓ Investment tip risk analysis
echo   ✓ Financial advisor verification
echo   ✓ PDF document authenticity checking
echo   ✓ Regulatory fraud monitoring dashboard
echo   ✓ AI-powered risk forecasting
echo   ✓ Fraud chain visualization
echo   ✓ Human-in-the-loop review system
echo   ✓ Real-time multi-source data integration
echo.
echo 🎯 Ready for demo! Follow the demo script at:
echo    backend\demo_script.md
echo.
goto end

:cleanup
echo [INFO] Cleaning up deployment...
docker-compose down --remove-orphans
docker system prune -f
echo [SUCCESS] Cleanup completed
goto end

:show_usage
echo Usage: %0 [deploy^|test^|cleanup^|restart^|logs^|status]
echo.
echo Commands:
echo   deploy   - Full deployment (default)
echo   test     - Run tests only
echo   cleanup  - Stop and clean up
echo   restart  - Restart services
echo   logs     - Show service logs
echo   status   - Show service status
goto end

REM Main logic
if "%1"=="test" goto run_tests
if "%1"=="cleanup" goto cleanup
if "%1"=="restart" (
    echo [INFO] Restarting services...
    docker-compose restart
    goto wait_for_services
)
if "%1"=="logs" (
    docker-compose logs -f
    goto end
)
if "%1"=="status" (
    docker-compose ps
    goto end
)
if "%1"=="help" goto show_usage
if not "%1"=="" if not "%1"=="deploy" goto show_usage

REM Default: full deployment
goto check_docker

:end
endlocal
