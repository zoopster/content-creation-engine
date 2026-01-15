@echo off
REM Content Creation Engine - MVP Setup and Test Script (Windows)
REM This script sets up the environment and validates the MVP deployment

echo ========================================
echo Content Creation Engine - MVP Setup
echo ========================================
echo.

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo [ERROR] requirements.txt not found
    echo Please run this script from the content-creation-engine directory
    pause
    exit /b 1
)

echo [OK] Running from project directory
echo.

REM Create virtual environment
echo ========================================
echo Setting Up Virtual Environment
echo ========================================
echo.

if exist venv (
    echo [WARNING] Virtual environment already exists
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo Using existing virtual environment
    )
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment ready
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo ========================================
echo Upgrading pip
echo ========================================
echo.
python -m pip install --upgrade pip --quiet
if %errorlevel% equ 0 (
    echo [OK] pip upgraded successfully
) else (
    echo [WARNING] pip upgrade failed (continuing anyway)
)
echo.

REM Install dependencies
echo ========================================
echo Installing Dependencies
echo ========================================
echo.
echo Installing required packages from requirements.txt...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] All dependencies installed
echo.

REM Verify key packages
echo Verifying key packages...
pip show pyyaml >nul 2>nul
if %errorlevel% equ 0 (echo [OK] pyyaml installed) else (echo [ERROR] pyyaml not found)

pip show python-docx >nul 2>nul
if %errorlevel% equ 0 (echo [OK] python-docx installed) else (echo [ERROR] python-docx not found)

pip show pytest >nul 2>nul
if %errorlevel% equ 0 (echo [OK] pytest installed) else (echo [ERROR] pytest not found)
echo.

REM Create output directory
if not exist output (
    echo Creating output directory...
    mkdir output
    echo [OK] Output directory created
)
echo.

REM Setup environment file
echo ========================================
echo Environment Configuration
echo ========================================
echo.

if not exist .env (
    if exist .env.example (
        echo Creating .env file from template...
        copy .env.example .env >nul
        echo [OK] .env file created
        echo.
        echo [WARNING] IMPORTANT: Edit .env and add your API keys before using LLM features
        echo   Required: ANTHROPIC_API_KEY or OPENAI_API_KEY
        echo   Edit with: notepad .env
        echo.
    ) else (
        echo [WARNING] .env.example not found - skipping environment setup
    )
) else (
    echo [OK] .env file already exists
)
echo.

REM Run MVP test
echo ========================================
echo Running MVP Test Suite
echo ========================================
echo.
echo Executing comprehensive validation tests...
echo.

python mvp_test.py
set TEST_EXIT_CODE=%errorlevel%

REM Summary
echo.
echo ========================================
echo Setup Complete
echo ========================================
echo.

if %TEST_EXIT_CODE% equ 0 (
    echo [OK] MVP is fully functional!
    echo.
    echo Next steps:
    echo   1. Add your API keys to .env file (for LLM features^)
    echo   2. Activate the virtual environment: venv\Scripts\activate.bat
    echo   3. Run examples:
    echo      - python examples\phase1_example.py (no API key needed^)
    echo      - python examples\phase2_endtoend.py (no API key needed^)
    echo      - python examples\multi_model_example.py (requires API key^)
    echo   4. Start the full stack:
    echo      - Backend: python -m uvicorn api.main:app --reload
    echo      - Frontend: cd frontend ^&^& npm install ^&^& npm run dev
    echo.
    echo Documentation:
    echo   - README.md - Complete setup and running instructions
    echo   - MVP_DEPLOYMENT.md - MVP deployment guide
    echo   - QUICKSTART.md - Quick start guide
    echo   - CLAUDE.md - Architecture overview
    echo.
    echo Environment is ready! Happy content creation!
    pause
    exit /b 0
) else (
    echo [ERROR] MVP tests failed
    echo.
    echo Troubleshooting steps:
    echo   1. Review the test output above for specific errors
    echo   2. Check MVP_DEPLOYMENT.md for troubleshooting guide
    echo   3. Verify Python version: python --version
    echo   4. Try reinstalling: rmdir /s /q venv then run setup_and_test.bat again
    echo.
    echo Need help? Check the documentation or open an issue on GitHub
    pause
    exit /b 1
)
