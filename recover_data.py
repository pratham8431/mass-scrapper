#!/usr/bin/env python3
"""
Data Recovery Script for YouTube Mass Scraper
Helps recover data and check scraper status
"""

import os
import csv
import glob
from datetime import datetime

def check_output_directory():
    """Check what files exist in the output directory"""
    print("🔍 Checking output directory...")
    
    if not os.path.exists('output'):
        print("❌ Output directory doesn't exist")
        return
    
    files = os.listdir('output')
    csv_files = [f for f in files if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ No CSV files found in output directory")
        return
    
    print(f"✅ Found {len(csv_files)} CSV files:")
    for file in sorted(csv_files):
        filepath = os.path.join('output', file)
        size = os.path.getsize(filepath)
        print(f"   📁 {file} ({size:,} bytes)")
        
        # Try to count rows
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                row_count = sum(1 for row in reader) - 1  # Subtract header
                print(f"      📊 {row_count:,} data rows")
        except Exception as e:
            print(f"      ❌ Error reading file: {e}")

def check_log_file():
    """Check the log file for recent activity"""
    print("\n📋 Checking log file...")
    
    if not os.path.exists('youtube_scraper.log'):
        print("❌ Log file doesn't exist")
        return
    
    try:
        with open('youtube_scraper.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            print("❌ Log file is empty")
            return
        
        print(f"✅ Log file has {len(lines):,} lines")
        
        # Find last progress update
        progress_lines = [line for line in lines if 'Progress:' in line]
        if progress_lines:
            last_progress = progress_lines[-1].strip()
            print(f"📊 Last progress: {last_progress}")
        
        # Find last timestamp
        if lines:
            last_line = lines[-1].strip()
            if last_line:
                print(f"🕐 Last activity: {last_line[:100]}...")
                
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def find_latest_data():
    """Find the most recent data file"""
    print("\n🔍 Finding latest data...")
    
    if not os.path.exists('output'):
        print("❌ Output directory doesn't exist")
        return None
    
    # Look for various file types
    patterns = [
        'output/checkpoint_*_influencers.csv',
        'output/emergency_save_*_influencers.csv',
        'output/emergency_exit_*_influencers.csv',
        'output/youtube_influencers_*.csv',
        'output/backup_*_influencers.csv'
    ]
    
    all_files = []
    for pattern in patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
    
    if not all_files:
        print("❌ No data files found")
        return None
    
    # Sort by modification time
    all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    print(f"✅ Found {len(all_files)} data files:")
    for i, file in enumerate(all_files[:5]):  # Show top 5
        mtime = os.path.getmtime(file)
        mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        size = os.path.getsize(file)
        print(f"   {i+1}. {os.path.basename(file)}")
        print(f"      📅 Modified: {mtime_str}")
        print(f"      📏 Size: {size:,} bytes")
    
    return all_files[0] if all_files else None

def show_data_preview(filename):
    """Show a preview of the data in a file"""
    if not filename:
        return
    
    print(f"\n👀 Preview of {os.path.basename(filename)}:")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            print(f"📋 Columns: {', '.join(header)}")
            
            # Show first few rows
            for i, row in enumerate(reader):
                if i >= 3:  # Show only first 3 rows
                    break
                print(f"   Row {i+1}: {row[:3]}...")  # Show first 3 columns
                
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    """Main recovery function"""
    print("🚀 YouTube Mass Scraper - Data Recovery Tool")
    print("=" * 50)
    
    # Check current state
    check_output_directory()
    check_log_file()
    
    # Find latest data
    latest_file = find_latest_data()
    
    if latest_file:
        show_data_preview(latest_file)
        
        print(f"\n💡 Recommendations:")
        print(f"   1. Your latest data is in: {os.path.basename(latest_file)}")
        print(f"   2. The scraper was likely interrupted before saving")
        print(f"   3. You can restart the scraper - it will now save every 100 influencers")
        print(f"   4. Use Ctrl+C to safely stop and save data")
    else:
        print(f"\n💡 No existing data found. You can start fresh with:")
        print(f"   python mass_scraper.py")

if __name__ == "__main__":
    main() 