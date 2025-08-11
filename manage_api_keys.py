#!/usr/bin/env python3
"""
YouTube API Key Management Utility
Helps validate and manage multiple YouTube Data API v3 keys
"""

import requests
import json
import time
from typing import List, Dict, Any
from config import YOUTUBE_API_KEYS

def validate_api_key(api_key: str) -> Dict[str, Any]:
    """
    Validate a single YouTube API key
    
    Args:
        api_key: YouTube Data API v3 key
        
    Returns:
        Dictionary with validation results
    """
    if not api_key or api_key == "YOUR_API_KEY_1_HERE":
        return {
            'valid': False,
            'error': 'Placeholder or empty key',
            'quota_remaining': 0
        }
    
    if not api_key.startswith('AIza'):
        return {
            'valid': False,
            'error': 'Invalid key format (should start with AIza)',
            'quota_remaining': 0
        }
    
    # Test the key with a simple API call
    test_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key': api_key,
        'part': 'snippet',
        'q': 'test',
        'type': 'channel',
        'maxResults': 1
    }
    
    try:
        response = requests.get(test_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            quota_remaining = response.headers.get('X-Quota-User', 'Unknown')
            
            return {
                'valid': True,
                'error': None,
                'quota_remaining': quota_remaining,
                'response_time': response.elapsed.total_seconds()
            }
        
        elif response.status_code == 403:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Unknown error')
            
            if 'quota' in error_message.lower():
                return {
                    'valid': True,
                    'error': 'Quota exceeded',
                    'quota_remaining': 0
                }
            else:
                return {
                    'valid': False,
                    'error': f'API error: {error_message}',
                    'quota_remaining': 0
                }
        
        else:
            return {
                'valid': False,
                'error': f'HTTP {response.status_code}: {response.text}',
                'quota_remaining': 0
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'valid': False,
            'error': f'Request error: {str(e)}',
            'quota_remaining': 0
        }

def test_all_api_keys() -> Dict[str, Any]:
    """
    Test all configured API keys
    
    Returns:
        Dictionary with test results for all keys
    """
    print("🔑 Testing all configured YouTube API keys...")
    print("=" * 60)
    
    results = {}
    valid_keys = []
    total_keys = len(YOUTUBE_API_KEYS)
    
    for i, key in enumerate(YOUTUBE_API_KEYS, 1):
        print(f"Testing key {i}/{total_keys}...")
        
        result = validate_api_key(key)
        results[f'key_{i}'] = result
        
        if result['valid']:
            status = "✅ VALID"
            valid_keys.append(key)
        else:
            status = "❌ INVALID"
        
        print(f"   {status}: {result.get('error', 'Working')}")
        
        # Rate limiting between tests
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"📊 Results Summary:")
    print(f"   Total keys: {total_keys}")
    print(f"   Valid keys: {len(valid_keys)}")
    print(f"   Invalid keys: {total_keys - len(valid_keys)}")
    
    if valid_keys:
        print(f"   ✅ Ready for scraping with {len(valid_keys)} keys")
    else:
        print("   ❌ No valid keys found - please check configuration")
    
    return results

def check_quota_status(api_keys: List[str]) -> Dict[str, Any]:
    """
    Check quota status for all valid API keys
    
    Args:
        api_keys: List of valid API keys
        
    Returns:
        Dictionary with quota information
    """
    print(f"\n📊 Checking quota status for {len(api_keys)} valid keys...")
    print("=" * 60)
    
    quota_info = {}
    
    for i, key in enumerate(api_keys, 1):
        print(f"Checking quota for key {i}...")
        
        # Make a test request to check quota
        test_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'key': key,
            'part': 'snippet',
            'q': 'quota test',
            'type': 'channel',
            'maxResults': 1
        }
        
        try:
            response = requests.get(test_url, params=params, timeout=10)
            
            if response.status_code == 200:
                quota_info[f'key_{i}'] = {
                    'status': 'active',
                    'quota_remaining': 'Available',
                    'response_time': response.elapsed.total_seconds()
                }
                print(f"   ✅ Active - Response time: {response.elapsed.total_seconds():.2f}s")
            
            elif response.status_code == 403:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                
                if 'quota' in error_message.lower():
                    quota_info[f'key_{i}'] = {
                        'status': 'quota_exceeded',
                        'quota_remaining': 0,
                        'error': error_message
                    }
                    print(f"   ⚠️  Quota exceeded")
                else:
                    quota_info[f'key_{i}'] = {
                        'status': 'error',
                        'quota_remaining': 0,
                        'error': error_message
                    }
                    print(f"   ❌ Error: {error_message}")
            
            else:
                quota_info[f'key_{i}'] = {
                    'status': 'error',
                    'quota_remaining': 0,
                    'error': f'HTTP {response.status_code}'
                }
                print(f"   ❌ HTTP {response.status_code}")
        
        except Exception as e:
            quota_info[f'key_{i}'] = {
                'status': 'error',
                'quota_remaining': 0,
                'error': str(e)
            }
            print(f"   ❌ Request failed: {str(e)}")
        
        # Rate limiting
        time.sleep(1)
    
    return quota_info

def generate_config_template(valid_keys: List[str]) -> str:
    """
    Generate a config.py template with valid keys
    
    Args:
        valid_keys: List of valid API keys
        
    Returns:
        String containing the config template
    """
    template = '''#!/usr/bin/env python3
"""
Configuration file for YouTube Mass Scraper
Contains API keys and other configuration settings
"""

# YouTube Data API v3 Keys ({} keys for rotation)
YOUTUBE_API_KEYS = [
'''
    
    for key in valid_keys:
        template += f'    "{key}",\n'
    
    template += ''']

# Scraping Configuration
SCRAPING_CONFIG = {
    'max_results_per_search': 50,  # Maximum results per search (API limit)
    'min_subscribers': 1000,       # Minimum subscriber count to include
    'rate_limit_delay': 0.1,       # Delay between API calls (seconds)
    'checkpoint_interval': 1000,   # Save checkpoint every N influencers
    'max_retries': 3,              # Maximum retries for failed requests
    'quota_reset_hours': 1,        # Hours to wait before resetting quota
}

# Search Configuration
SEARCH_CONFIG = {
    'published_after': '2010-01-01T00:00:00Z',  # Only channels created after this date
    'order_by': 'relevance',                     # Search result ordering
    'search_type': 'channel',                    # Type of search results
}

# Output Configuration
OUTPUT_CONFIG = {
    'csv_encoding': 'utf-8',
    'include_timestamp': True,
    'backup_interval': 500,        # Backup every N influencers
    'max_description_length': 500,  # Truncate descriptions to this length
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file_logging': True,
    'log_file': 'youtube_scraper.log',
    'max_log_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}
'''
    
    return template

def main():
    """Main function"""
    print("🔑 YouTube API Key Management Utility")
    print("=" * 60)
    
    # Test all configured keys
    results = test_all_api_keys()
    
    # Extract valid keys
    valid_keys = []
    for i, key in enumerate(YOUTUBE_API_KEYS, 1):
        if results[f'key_{i}']['valid']:
            valid_keys.append(key)
    
    if not valid_keys:
        print("\n❌ No valid API keys found!")
        print("💡 Please:")
        print("   1. Get YouTube Data API v3 keys from Google Cloud Console")
        print("   2. Update config.py with your actual keys")
        print("   3. Run this utility again to validate")
        return
    
    # Check quota status
    quota_info = check_quota_status(valid_keys)
    
    # Show recommendations
    print(f"\n💡 Recommendations:")
    print(f"   • You have {len(valid_keys)} valid API keys")
    
    active_keys = sum(1 for info in quota_info.values() if info['status'] == 'active')
    print(f"   • {active_keys} keys are currently active")
    
    if len(valid_keys) < 5:
        print(f"   • Consider adding more keys for better performance")
        print(f"   • With {len(valid_keys)} keys, expect ~{len(valid_keys) * 50} influencers/hour")
    else:
        print(f"   • Excellent! With {len(valid_keys)} keys, expect ~{len(valid_keys) * 50} influencers/hour")
    
    # Offer to generate new config
    if valid_keys:
        print(f"\n💾 Generate new config.py with valid keys? (y/N): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            config_content = generate_config_template(valid_keys)
            
            # Backup existing config
            import shutil
            if os.path.exists('config.py'):
                shutil.copy('config.py', 'config.py.backup')
                print("   📁 Backed up existing config.py to config.py.backup")
            
            # Write new config
            with open('config.py', 'w') as f:
                f.write(config_content)
            
            print("   ✅ Generated new config.py with valid keys")
            print("   💡 You can now run the scraper!")

if __name__ == "__main__":
    main() 