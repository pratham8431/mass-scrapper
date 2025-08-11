#!/usr/bin/env python3
"""
Mass Scraper for 10K YouTube Influencers
High-volume scraping with efficient data storage and CSV export
"""

import csv
import time
import random
import logging
import os
import signal
import sys
from typing import List, Dict, Any
from datetime import datetime
from youtube_scraper import YouTubeInfluencerScraper
from config import YOUTUBE_API_KEYS, SCRAPING_CONFIG, OUTPUT_CONFIG, LOGGING_CONFIG

# Global variables for signal handling
scraper_instance = None
current_influencers = []
is_running = False

def signal_handler(signum, frame):
    """Handle interrupt signals to save data before exit"""
    global scraper_instance, current_influencers, is_running
    
    if is_running and current_influencers:
        logger = logging.getLogger(__name__)
        logger.info(f"\n⚠️  Received interrupt signal {signum}")
        logger.info(f"💾 Saving {len(current_influencers)} influencers before exit...")
        
        # Save emergency backup
        emergency_file = f"emergency_exit_{len(current_influencers)}_influencers.csv"
        save_to_csv(current_influencers, emergency_file)
        logger.info(f"🚨 Emergency exit save: {emergency_file}")
        
        # Close scraper gracefully
        if scraper_instance:
            scraper_instance.close()
        
        logger.info("✅ Data saved safely. Exiting...")
        sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler) # Termination signal

def setup_logging():
    """Setup logging configuration"""
    log_level = getattr(logging, LOGGING_CONFIG['level'])
    log_format = logging.Formatter(LOGGING_CONFIG['format'])
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    
    # File handler
    if LOGGING_CONFIG['file_logging']:
        file_handler = logging.FileHandler(LOGGING_CONFIG['log_file'])
        file_handler.setFormatter(log_format)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    if LOGGING_CONFIG['file_logging']:
        root_logger.addHandler(file_handler)
    
    return root_logger

def create_mass_search_configs():
    """Create configurations for mass scraping across categories and cities"""
    return [
        # Beauty & Fashion
        {"category": "beauty", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney"]},
        {"category": "makeup", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris"]},
        {"category": "fashion", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Milan", "Tokyo"]},
        {"category": "skincare", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        
        # Technology
        {"category": "tech", "cities": ["Mumbai", "Delhi", "Bangalore", "Chennai", "New York", "San Francisco", "London", "Tokyo", "Berlin"]},
        {"category": "programming", "cities": ["Mumbai", "Delhi", "Bangalore", "Chennai", "New York", "San Francisco", "London", "Tokyo"]},
        {"category": "gadgets", "cities": ["Mumbai", "Delhi", "New York", "San Francisco", "London", "Tokyo", "Berlin"]},
        {"category": "ai", "cities": ["Mumbai", "Delhi", "Bangalore", "New York", "San Francisco", "London", "Tokyo"]},
        
        # Gaming & Entertainment
        {"category": "gaming", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Tokyo", "Berlin", "Sydney"]},
        {"category": "esports", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Tokyo", "Berlin"]},
        {"category": "streaming", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Tokyo", "Berlin"]},
        
        # Fitness & Health
        {"category": "fitness", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney"]},
        {"category": "yoga", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "nutrition", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "wellness", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        
        # Food & Cooking
        {"category": "food", "cities": ["Mumbai", "Delhi", "Bangalore", "Chennai", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney"]},
        {"category": "cooking", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "baking", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "restaurant", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney"]},
        
        # Travel & Lifestyle
        {"category": "travel", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney", "Berlin"]},
        {"category": "lifestyle", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney"]},
        {"category": "vlog", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney"]},
        
        # Education & Learning
        {"category": "education", "cities": ["Mumbai", "Delhi", "Bangalore", "Chennai", "New York", "London", "Tokyo", "Berlin"]},
        {"category": "tutorials", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "courses", "cities": ["Mumbai", "Delhi", "Bangalore", "New York", "London", "Tokyo"]},
        
        # Business & Finance
        {"category": "business", "cities": ["Mumbai", "Delhi", "Bangalore", "Chennai", "New York", "London", "Tokyo", "Berlin"]},
        {"category": "finance", "cities": ["Mumbai", "Delhi", "New York", "London", "Tokyo", "Berlin"]},
        {"category": "entrepreneur", "cities": ["Mumbai", "Delhi", "Bangalore", "New York", "London", "Tokyo", "Berlin"]},
        
        # Music & Arts
        {"category": "music", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney"]},
        {"category": "art", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "dance", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        
        # Sports & Athletics
        {"category": "sports", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney"]},
        {"category": "workout", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        
        # Automotive & Cars
        {"category": "automotive", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Berlin"]},
        {"category": "cars", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Berlin"]},
        {"category": "bikes", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        
        # Parenting & Family
        {"category": "parenting", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "family", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "kids", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        
        # Science & Technology
        {"category": "science", "cities": ["Mumbai", "Delhi", "New York", "London", "Tokyo", "Berlin"]},
        {"category": "research", "cities": ["Mumbai", "Delhi", "New York", "London", "Tokyo", "Berlin"]},
        {"category": "innovation", "cities": ["Mumbai", "Delhi", "Bangalore", "New York", "San Francisco", "London", "Tokyo"]},
        
        # Comedy & Entertainment
        {"category": "comedy", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "entertainment", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo", "Sydney"]},
        {"category": "funny", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        
        # DIY & Crafts
        {"category": "diy", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "crafts", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "hacks", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        
        # Reviews & Testing
        {"category": "reviews", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "testing", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
        {"category": "unboxing", "cities": ["Mumbai", "Delhi", "Los Angeles", "New York", "London", "Paris", "Tokyo"]},
    ]

def get_country_from_city(city: str) -> str:
    """Get country from city name"""
    city_country_map = {
        # India
        "Mumbai": "India", "Delhi": "India", "Bangalore": "India", 
        "Chennai": "India", "Hyderabad": "India", "Kolkata": "India",
        
        # USA
        "Los Angeles": "USA", "New York": "USA", "Chicago": "USA",
        "Houston": "USA", "Phoenix": "USA", "Philadelphia": "USA",
        "San Antonio": "USA", "San Diego": "USA", "Dallas": "USA",
        "San Jose": "USA", "San Francisco": "USA",
        
        # UK
        "London": "UK", "Manchester": "UK", "Birmingham": "UK",
        "Leeds": "UK", "Liverpool": "UK", "Brighton": "UK",
        
        # Europe
        "Paris": "France", "Marseille": "France", "Lyon": "France",
        "Berlin": "Germany", "Hamburg": "Germany", "Munich": "Germany",
        "Milan": "Italy", "Rome": "Italy",
        
        # Asia-Pacific
        "Tokyo": "Japan", "Osaka": "Japan", "Yokohama": "Japan",
        "Sydney": "Australia", "Melbourne": "Australia", "Brisbane": "Australia",
        
        # Canada
        "Toronto": "Canada", "Montreal": "Canada", "Vancouver": "Canada"
    }
    
    return city_country_map.get(city, "Unknown")

def get_category_mapping():
    """Map search terms to database categories"""
    return {
        "beauty": "Beauty & Cosmetics", "makeup": "Beauty & Cosmetics",
        "skincare": "Beauty & Cosmetics", "fashion": "Fashion & Style",
        "tech": "Technology & Gadgets", "programming": "Technology & Gadgets",
        "gadgets": "Technology & Gadgets", "ai": "Technology & Gadgets",
        "gaming": "Gaming & Esports", "esports": "Gaming & Esports",
        "streaming": "Gaming & Esports", "fitness": "Fitness & Health",
        "yoga": "Fitness & Health", "nutrition": "Fitness & Health",
        "wellness": "Fitness & Health", "food": "Food & Cooking",
        "cooking": "Food & Cooking", "baking": "Food & Cooking",
        "restaurant": "Food & Cooking", "travel": "Travel & Lifestyle",
        "lifestyle": "Travel & Lifestyle", "vlog": "Travel & Lifestyle",
        "education": "Education & Learning", "tutorials": "Education & Learning",
        "courses": "Education & Learning", "business": "Business & Finance",
        "finance": "Business & Finance", "entrepreneur": "Business & Finance",
        "music": "Music & Arts", "art": "Music & Arts", "dance": "Music & Arts",
        "sports": "Sports & Athletics", "workout": "Sports & Athletics",
        "automotive": "Automotive & Cars", "cars": "Automotive & Cars",
        "bikes": "Automotive & Cars", "parenting": "Parenting & Family",
        "family": "Parenting & Family", "kids": "Parenting & Family",
        "science": "Science & Technology", "research": "Science & Technology",
        "innovation": "Science & Technology", "comedy": "Entertainment & Comedy",
        "entertainment": "Entertainment & Comedy", "funny": "Entertainment & Comedy",
        "diy": "DIY & Crafts", "crafts": "DIY & Crafts", "hacks": "DIY & Crafts",
        "reviews": "Reviews & Testing", "testing": "Reviews & Testing",
        "unboxing": "Reviews & Testing"
    }

def get_niche_mapping():
    """Map search terms to database niches"""
    return {
        "beauty": "beauty", "makeup": "beauty", "skincare": "beauty",
        "fashion": "fashion", "tech": "tech", "programming": "tech",
        "gadgets": "tech", "ai": "tech", "gaming": "gaming",
        "esports": "gaming", "streaming": "gaming", "fitness": "fitness",
        "yoga": "fitness", "nutrition": "fitness", "wellness": "fitness",
        "food": "food", "cooking": "food", "baking": "food",
        "restaurant": "food", "travel": "travel", "lifestyle": "travel",
        "vlog": "travel", "education": "education", "tutorials": "education",
        "courses": "education", "business": "business", "finance": "business",
        "entrepreneur": "business", "music": "music", "art": "music",
        "dance": "music", "sports": "sports", "workout": "sports",
        "automotive": "automotive", "cars": "automotive", "bikes": "automotive",
        "parenting": "parenting", "family": "parenting", "kids": "parenting",
        "science": "science", "research": "science", "innovation": "science",
        "comedy": "entertainment", "entertainment": "entertainment", "funny": "entertainment",
        "diy": "diy", "crafts": "diy", "hacks": "diy",
        "reviews": "reviews", "testing": "reviews", "unboxing": "reviews"
    }

def calculate_engagement_rate(stats: Dict[str, Any]) -> float:
    """Calculate engagement rate based on available data"""
    try:
        subscriber_count = int(stats.get('subscriberCount', 0))
        view_count = int(stats.get('viewCount', 0))
        
        if subscriber_count == 0:
            return 0.0
        
        engagement = (view_count / subscriber_count) * 100
        return min(max(engagement, 0.1), 15.0)
        
    except:
        return 5.0

def scrape_influencers_batch(scraper: YouTubeInfluencerScraper, category: str, city: str, 
                           max_results: int = 50, min_subscribers: int = 1000):
    """Scrape a batch of influencers for a specific category and city"""
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 Scraping {category} influencers in {city}...")
    
    try:
        search_query = f"{city} {category}"
        channels = scraper.search_channels(city, category, max_results=max_results)
        
        if not channels:
            logger.warning(f"   ❌ No channels found for {search_query}")
            return []
        
        logger.info(f"   ✅ Found {len(channels)} channels")
        
        influencers = []
        for channel in channels:
            try:
                stats = scraper.get_channel_statistics(channel['channelId'])
                if not stats:
                    continue
                
                subscriber_count = int(stats.get('subscriberCount', 0))
                if subscriber_count < min_subscribers:
                    continue
                
                # Truncate description if too long
                description = stats.get('description', '')[:OUTPUT_CONFIG['max_description_length']]
                
                influencer = {
                    'channel_id': channel['channelId'],
                    'channel_title': stats['channelTitle'],
                    'description': description,
                    'subscriber_count': subscriber_count,
                    'view_count': int(stats.get('viewCount', 0)),
                    'video_count': int(stats.get('videoCount', 0)),
                    'published_at': stats.get('publishedAt', ''),
                    'category': get_category_mapping().get(category, 'Other'),
                    'city': city,
                    'country': get_country_from_city(city),
                    'niche': get_niche_mapping().get(category, 'other'),
                    'engagement_rate': calculate_engagement_rate(stats),
                    'search_query': search_query,
                    'scraped_at': datetime.now().isoformat()
                }
                
                influencers.append(influencer)
                logger.info(f"   ✅ Added: {influencer['channel_title']} ({influencer['subscriber_count']:,} subscribers)")
                
                # Rate limiting
                time.sleep(SCRAPING_CONFIG['rate_limit_delay'])
                
            except Exception as e:
                logger.error(f"   ❌ Error processing channel: {str(e)}")
                continue
        
        return influencers
        
    except Exception as e:
        logger.error(f"   ❌ Error scraping {category} in {city}: {str(e)}")
        return []

def save_to_csv(influencers: List[Dict], filename: str):
    """Save influencers to CSV file"""
    logger = logging.getLogger(__name__)
    
    if not influencers:
        logger.warning("❌ No influencers to save")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    filepath = os.path.join('output', filename)
    
    fieldnames = [
        'channel_id', 'channel_title', 'description', 'subscriber_count',
        'view_count', 'video_count', 'published_at', 'category', 'city',
        'country', 'niche', 'engagement_rate', 'search_query', 'scraped_at'
    ]
    
    try:
        with open(filepath, 'w', newline='', encoding=OUTPUT_CONFIG['csv_encoding']) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(influencers)
        
        logger.info(f"💾 Saved {len(influencers)} influencers to {filepath}")
        
    except Exception as e:
        logger.error(f"❌ Error saving CSV: {str(e)}")

def find_latest_checkpoint():
    """Find the latest checkpoint file to resume from"""
    output_dir = 'output'
    if not os.path.exists(output_dir):
        return None
    
    checkpoint_files = []
    for filename in os.listdir(output_dir):
        if filename.startswith('checkpoint_') and filename.endswith('_influencers.csv'):
            try:
                # Extract number from filename like "checkpoint_1500_influencers.csv"
                parts = filename.split('_')
                if len(parts) >= 2:
                    count = int(parts[1])
                    checkpoint_files.append((count, filename))
            except ValueError:
                continue
    
    if not checkpoint_files:
        return None
    
    # Return the file with highest count
    latest = max(checkpoint_files, key=lambda x: x[0])
    return latest[1], latest[0]

def load_checkpoint_data(checkpoint_file: str):
    """Load data from a checkpoint file"""
    logger = logging.getLogger(__name__)
    filepath = os.path.join('output', checkpoint_file)
    
    if not os.path.exists(filepath):
        logger.warning(f"❌ Checkpoint file not found: {filepath}")
        return []
    
    try:
        influencers = []
        with open(filepath, 'r', newline='', encoding=OUTPUT_CONFIG['csv_encoding']) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                influencers.append(row)
        
        logger.info(f"✅ Loaded {len(influencers)} influencers from checkpoint: {checkpoint_file}")
        return influencers
        
    except Exception as e:
        logger.error(f"❌ Error loading checkpoint: {str(e)}")
        return []

def mass_scrape_10k(api_keys: List[str], target_count: int = 10000, max_per_search: int = 50):
    """Main function to scrape 10K influencers"""
    global scraper_instance, current_influencers, is_running
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Mass Scraper for 10K YouTube Influencers")
    logger.info("=" * 60)
    
    try:
        scraper = YouTubeInfluencerScraper(api_keys)
        scraper_instance = scraper  # Store globally for signal handling
        is_running = True
        logger.info(f"✅ Scraper initialized with {len(api_keys)} API keys")
        
        # Show API key status
        status = scraper.get_api_key_status()
        logger.info(f"📊 API Key Status: {status['total_keys']} keys available")
        
        configs = create_mass_search_configs()
        logger.info(f"📋 Found {len(configs)} category-city combinations")
        
        all_influencers = []
        current_influencers = all_influencers  # Store globally for signal handling
        total_searches = 0
        start_time = datetime.now()
        
        for config in configs:
            category = config['category']
            cities = config['cities']
            
            logger.info(f"\n🏷️  Processing category: {category}")
            logger.info(f"   Cities: {', '.join(cities)}")
            
            for city in cities:
                if len(all_influencers) >= target_count:
                    break
                
                total_searches += 1
                batch = scrape_influencers_batch(scraper, category, city, max_per_search, SCRAPING_CONFIG['min_subscribers'])
                all_influencers.extend(batch)
                
                # Show progress
                elapsed_time = datetime.now() - start_time
                rate = len(all_influencers) / (elapsed_time.total_seconds() / 3600) if elapsed_time.total_seconds() > 0 else 0
                
                logger.info(f"   📊 Progress: {len(all_influencers)}/{target_count} influencers collected")
                logger.info(f"   🔍 Searches completed: {total_searches}")
                logger.info(f"   ⏱️  Rate: {rate:.1f} influencers/hour")
                
                # Save checkpoint (reduced interval for better data safety)
                if len(all_influencers) % SCRAPING_CONFIG['checkpoint_interval'] == 0 and len(all_influencers) > 0:
                    checkpoint_file = f"checkpoint_{len(all_influencers)}_influencers.csv"
                    save_to_csv(all_influencers, checkpoint_file)
                    logger.info(f"   💾 Checkpoint saved: {checkpoint_file}")
                
                # Emergency save (every 50 influencers for maximum safety)
                if len(all_influencers) % SCRAPING_CONFIG['emergency_save_interval'] == 0 and len(all_influencers) > 0:
                    emergency_file = f"emergency_save_{len(all_influencers)}_influencers.csv"
                    save_to_csv(all_influencers, emergency_file)
                    logger.info(f"   🚨 Emergency save: {emergency_file}")
                
                # Show API key status periodically
                if total_searches % 10 == 0:
                    status = scraper.get_api_key_status()
                    active_keys = sum(1 for key_info in status['keys_status'].values() if not key_info['quota_exceeded'])
                    logger.info(f"   🔑 Active API keys: {active_keys}/{status['total_keys']}")
                
                time.sleep(2)  # Rate limiting between searches
            
            if len(all_influencers) >= target_count:
                break
        
        # Final save
        final_filename = f"youtube_influencers_{len(all_influencers)}.csv"
        save_to_csv(all_influencers, final_filename)
        
        # Also save a timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}_{len(all_influencers)}_influencers.csv"
        save_to_csv(all_influencers, backup_filename)
        
        total_time = datetime.now() - start_time
        logger.info(f"\n🎉 Mass Scraping Complete!")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   • Total influencers collected: {len(all_influencers)}")
        logger.info(f"   • Total searches performed: {total_searches}")
        logger.info(f"   • Total time: {total_time}")
        logger.info(f"   • Average rate: {len(all_influencers) / (total_time.total_seconds() / 3600):.1f} influencers/hour")
        logger.info(f"   • Final file: {final_filename}")
        logger.info(f"   • Backup file: {backup_filename}")
        
        return len(all_influencers)
        
    except Exception as e:
        logger.error(f"❌ Error during mass scraping: {str(e)}")
        return 0
    finally:
        if 'scraper' in locals():
            scraper.close()
        
        # Reset global variables
        scraper_instance = None
        current_influencers = []
        is_running = False

def main():
    """Main function"""
    logger = setup_logging()
    logger.info("🎯 Mass Scraper for 10K YouTube Influencers")
    logger.info("=" * 60)
    
    # Check for existing checkpoints
    checkpoint_info = find_latest_checkpoint()
    if checkpoint_info:
        checkpoint_file, checkpoint_count = checkpoint_info
        logger.info(f"📁 Found existing checkpoint: {checkpoint_file} ({checkpoint_count} influencers)")
        
        resume = input(f"🔄 Resume from checkpoint? (y/N): ").strip().lower()
        if resume in ['y', 'yes']:
            logger.info(f"🔄 Resuming from checkpoint: {checkpoint_file}")
            # Load checkpoint data
            checkpoint_data = load_checkpoint_data(checkpoint_file)
            if checkpoint_data:
                logger.info(f"✅ Loaded {len(checkpoint_data)} influencers from checkpoint")
                # Continue with existing data
                # TODO: Implement resume logic
                logger.info("⚠️  Resume functionality coming soon. Starting fresh for now.")
            else:
                logger.warning("⚠️  Failed to load checkpoint. Starting fresh.")
    
    # Check if API keys are configured
    if not YOUTUBE_API_KEYS or YOUTUBE_API_KEYS[0] == "YOUR_API_KEY_1_HERE":
        logger.error("❌ YouTube API keys not configured in config.py")
        logger.info("💡 Please update config.py with your actual API keys:")
        logger.info("   YOUTUBE_API_KEYS = ['key1', 'key2', ...]")
        return
    
    # Filter out placeholder keys
    valid_keys = [key for key in YOUTUBE_API_KEYS if key != "YOUR_API_KEY_1_HERE" and key.startswith("AIza")]
    
    if not valid_keys:
        logger.error("❌ No valid YouTube API keys found")
        logger.info("💡 Please add valid API keys to config.py")
        return
    
    logger.info(f"✅ Found {len(valid_keys)} valid API keys")
    
    print("\n🔧 Configuration:")
    try:
        target_count = int(input("Enter target number of influencers (default 10000): ") or "10000")
        max_per_search = int(input("Enter max results per search (default 50): ") or "50")
    except ValueError:
        target_count = 10000
        max_per_search = 50
    
    logger.info(f"📊 Will collect {target_count:,} influencers with {max_per_search} per search")
    
    confirm = input("\n🚀 Start mass scraping? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        logger.info("❌ Mass scraping cancelled")
        return
    
    logger.info("\n🚀 Starting mass scraping process...")
    logger.info("⚠️  This will take several hours due to API rate limits")
    logger.info("💡 Progress will be saved every 100 influencers")
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

if __name__ == "__main__":
    main() 