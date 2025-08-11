#!/usr/bin/env python3
"""
Automated Mass Scraper for YouTube Influencers
Runs with default settings without user interaction
"""

import logging
import os
from datetime import datetime
from mass_scraper import mass_scrape_10k, setup_logging
from config import YOUTUBE_API_KEYS

def main():
    """Automated main function with default settings"""
    logger = setup_logging()
    logger.info("🚀 Starting Automated Mass Scraper for YouTube Influencers")
    logger.info("=" * 60)
    
    # Default settings
    target_count = 10000
    max_per_search = 50
    
    logger.info(f"📊 Configuration:")
    logger.info(f"   • Target influencers: {target_count:,}")
    logger.info(f"   • Max per search: {max_per_search}")
    logger.info(f"   • API keys available: {len(YOUTUBE_API_KEYS)}")
    
    # Filter out placeholder keys
    valid_keys = [key for key in YOUTUBE_API_KEYS if key != "YOUR_API_KEY_1_HERE" and key.startswith("AIza")]
    
    if not valid_keys:
        logger.error("❌ No valid YouTube API keys found")
        return
    
    logger.info(f"✅ Found {len(valid_keys)} valid API keys")
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    logger.info("\n🚀 Starting mass scraping process...")
    logger.info("⚠️  This will take several hours due to API rate limits")
    logger.info("💡 Progress will be saved every 1000 influencers")
    logger.info("💡 You can stop anytime with Ctrl+C")
    
    try:
        collected = mass_scrape_10k(valid_keys, target_count, max_per_search)
        
        if collected > 0:
            logger.info(f"\n🎉 Successfully collected {collected:,} influencers!")
            logger.info("💡 Files created:")
            logger.info(f"   • Final CSV: output/youtube_influencers_{collected}.csv")
            logger.info("   • Checkpoint files: output/checkpoint_*_influencers.csv")
        else:
            logger.warning("\n⚠️  No influencers were collected")
    
    except KeyboardInterrupt:
        logger.info("\n⏹️  Mass scraping stopped by user")
        logger.info("💾 Progress has been saved in checkpoint files")
    except Exception as e:
        logger.error(f"\n❌ Error during mass scraping: {str(e)}")

if __name__ == "__main__":
    main() 