#!/usr/bin/env python3
"""
Test script for YouTube Influencer Scraper
Tests basic functionality with a small sample
"""

import sys
import os
from youtube_scraper import YouTubeInfluencerScraper
from config import YOUTUBE_API_KEYS

def test_api_keys():
    """Test if API keys are properly configured"""
    print("🔑 Testing API key configuration...")
    
    if not YOUTUBE_API_KEYS or YOUTUBE_API_KEYS[0] == "YOUR_API_KEY_1_HERE":
        print("❌ API keys not configured in config.py")
        print("💡 Please update config.py with your actual API keys")
        return False
    
    # Filter out placeholder keys
    valid_keys = [key for key in YOUTUBE_API_KEYS if key != "YOUR_API_KEY_1_HERE" and key.startswith("AIza")]
    
    if not valid_keys:
        print("❌ No valid API keys found")
        return False
    
    print(f"✅ Found {len(valid_keys)} valid API keys")
    return valid_keys

def test_basic_search(api_keys):
    """Test basic channel search functionality"""
    print("\n🔍 Testing basic channel search...")
    
    try:
        scraper = YouTubeInfluencerScraper(api_keys[:3])  # Use first 3 keys for testing
        
        # Test search for a simple category
        print("   Searching for 'tech' channels in 'Mumbai'...")
        channels = scraper.search_channels("Mumbai", "tech", max_results=5)
        
        if channels:
            print(f"   ✅ Found {len(channels)} channels")
            for i, channel in enumerate(channels[:3]):  # Show first 3
                print(f"      {i+1}. {channel['channelTitle']} (ID: {channel['channelId'][:20]}...)")
        else:
            print("   ❌ No channels found")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error during search: {str(e)}")
        return False
    finally:
        if 'scraper' in locals():
            scraper.close()

def test_channel_statistics(api_keys):
    """Test channel statistics retrieval"""
    print("\n📊 Testing channel statistics retrieval...")
    
    try:
        scraper = YouTubeInfluencerScraper(api_keys[:3])
        
        # First get a channel ID
        channels = scraper.search_channels("Mumbai", "tech", max_results=1)
        if not channels:
            print("   ❌ No channels found for testing")
            return False
        
        channel_id = channels[0]['channelId']
        print(f"   Testing with channel: {channels[0]['channelTitle']}")
        
        # Get statistics
        stats = scraper.get_channel_statistics(channel_id)
        if stats:
            print("   ✅ Channel statistics retrieved successfully")
            print(f"      Title: {stats['channelTitle']}")
            print(f"      Subscribers: {stats.get('subscriberCount', 'N/A'):,}")
            print(f"      Views: {stats.get('viewCount', 'N/A'):,}")
            print(f"      Videos: {stats.get('videoCount', 'N/A')}")
            print(f"      Category: {stats.get('category', 'N/A')}")
            print(f"      Country: {stats.get('country', 'N/A')}")
        else:
            print("   ❌ Failed to retrieve channel statistics")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error during statistics retrieval: {str(e)}")
        return False
    finally:
        if 'scraper' in locals():
            scraper.close()

def test_api_key_rotation(api_keys):
    """Test API key rotation functionality"""
    print("\n🔄 Testing API key rotation...")
    
    try:
        scraper = YouTubeInfluencerScraper(api_keys)
        
        # Show initial status
        status = scraper.get_api_key_status()
        print(f"   Total keys: {status['total_keys']}")
        print(f"   Current key index: {status['current_key_index']}")
        
        # Make a few requests to see rotation in action
        print("   Making test requests to see key rotation...")
        for i in range(3):
            channels = scraper.search_channels("Delhi", "fashion", max_results=1)
            current_status = scraper.get_api_key_status()
            print(f"      Request {i+1}: Using key {current_status['current_key_index'] + 1}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error during key rotation test: {str(e)}")
        return False
    finally:
        if 'scraper' in locals():
            scraper.close()

def main():
    """Main test function"""
    print("🧪 YouTube Influencer Scraper Test Suite")
    print("=" * 50)
    
    # Test 1: API Key Configuration
    api_keys = test_api_keys()
    if not api_keys:
        print("\n❌ Test failed: API keys not configured")
        return
    
    # Test 2: Basic Search
    if not test_basic_search(api_keys):
        print("\n❌ Test failed: Basic search functionality")
        return
    
    # Test 3: Channel Statistics
    if not test_channel_statistics(api_keys):
        print("\n❌ Test failed: Channel statistics retrieval")
        return
    
    # Test 4: API Key Rotation
    if not test_api_key_rotation(api_keys):
        print("\n❌ Test failed: API key rotation")
        return
    
    print("\n🎉 All tests passed! The scraper is working correctly.")
    print("💡 You can now run the full mass scraper with:")
    print("   python mass_scraper.py")

if __name__ == "__main__":
    main() 