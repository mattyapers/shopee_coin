@echo off
echo Setting up Shopee Review Generator...

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

if not exist .env (
    copy .env.example .env >nul
    echo.
    echo Created .env from template.
    echo Edit .env and add your GEMINI_API_KEY.
    echo Get a free key at: https://aistudio.google.com/app/apikey
)

echo.
echo Setup complete! Run run.bat to generate reviews.
pause
