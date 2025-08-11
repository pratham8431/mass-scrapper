@echo off
chcp 65001 >nul
title YouTube Mass Influencer Scraper

echo 🚀 YouTube Mass Influencer Scraper
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found
    echo 💡 Please run this script from the project directory
    pause
    exit /b 1
)

if not exist "config.py" (
    echo ❌ config.py not found
    echo 💡 Please configure your API keys first
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 📦 Checking dependencies...
python -c "import requests, pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📥 Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        echo 💡 Please check your Python environment
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully!
) else (
    echo ✅ Dependencies already installed!
)

REM Check API key configuration
echo 🔑 Checking API key configuration...
python -c "from config import YOUTUBE_API_KEYS; valid_keys = [k for k in YOUTUBE_API_KEYS if k != 'YOUR_API_KEY_1_HERE' and k.startswith('AIza')]; exit(0 if valid_keys else 1)"
if %errorlevel% neq 0 (
    echo ❌ No valid API keys found in config.py
    echo 💡 Please update config.py with your actual YouTube API keys
    pause
    exit /b 1
)

REM Create output directory
if not exist "output" mkdir output

REM Show menu
echo.
echo 🔧 Choose an option:
echo 1. Test the scraper (recommended first)
echo 2. Run full mass scraping (10K+ influencers)
echo 3. Manage API keys
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo 🧪 Running scraper test...
    python test_scraper.py
) else if "%choice%"=="2" (
    echo 🚀 Starting mass scraping...
    echo ⚠️  This will take several hours and collect 10K+ influencers
    echo 💡 Progress will be saved every 1000 influencers
    echo 💡 You can stop anytime with Ctrl+C
    echo.
    set /p confirm="Continue? (y/N): "
    if /i "%confirm%"=="y" (
        python mass_scraper.py
    ) else (
        echo ❌ Mass scraping cancelled
    )
) else if "%choice%"=="3" (
    echo 🔑 Running API key management utility...
    python manage_api_keys.py
) else if "%choice%"=="4" (
    echo 👋 Goodbye!
    exit /b 0
) else (
    echo ❌ Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
echo ✅ Script completed!
echo 💡 Check the 'output' directory for generated CSV files
echo 💡 Check 'youtube_scraper.log' for detailed logs
pause 