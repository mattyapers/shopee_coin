@echo off
echo Setting up Shopee Review Generator (OCR-based)...

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo.
echo Setup complete! Run run.bat to generate reviews.
pause
