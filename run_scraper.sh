#!/bin/bash

# YouTube Mass Scraper Runner Script
# This script helps you run the YouTube influencer scraper easily

echo "🚀 YouTube Mass Influencer Scraper"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if required files exist
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run this script from the project directory."
    exit 1
fi

if [ ! -f "config.py" ]; then
    echo "❌ config.py not found. Please configure your API keys first."
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
if ! python3 -c "import requests, pandas" &> /dev/null; then
    echo "📥 Installing required packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please check your Python environment."
        exit 1
    fi
    echo "✅ Dependencies installed successfully!"
else
    echo "✅ Dependencies already installed!"
fi

# Check API key configuration
echo "🔑 Checking API key configuration..."
python3 -c "
from config import YOUTUBE_API_KEYS
valid_keys = [k for k in YOUTUBE_API_KEYS if k != 'YOUR_API_KEY_1_HERE' and k.startswith('AIza')]
if not valid_keys:
    print('❌ No valid API keys found in config.py')
    print('💡 Please update config.py with your actual YouTube API keys')
    exit(1)
else:
    print(f'✅ Found {len(valid_keys)} valid API keys')
"

if [ $? -ne 0 ]; then
    echo "❌ API key configuration failed. Please fix config.py first."
    exit 1
fi

# Create output directory
mkdir -p output

# Show menu
echo ""
echo "🔧 Choose an option:"
echo "1. Test the scraper (recommended first)"
echo "2. Run full mass scraping (10K+ influencers)"
echo "3. Manage API keys"
echo "4. Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🧪 Running scraper test..."
        python3 test_scraper.py
        ;;
    2)
        echo "🚀 Starting mass scraping..."
        echo "⚠️  This will take several hours and collect 10K+ influencers"
        echo "💡 Progress will be saved every 1000 influencers"
        echo "💡 You can stop anytime with Ctrl+C"
        echo ""
        read -p "Continue? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            python3 mass_scraper.py
        else
            echo "❌ Mass scraping cancelled"
        fi
        ;;
    3)
        echo "🔑 Running API key management utility..."
        python3 manage_api_keys.py
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Script completed!"
echo "💡 Check the 'output' directory for generated CSV files"
echo "💡 Check 'youtube_scraper.log' for detailed logs" 