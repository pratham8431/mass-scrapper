# YouTube Mass Influencer Scraper 🚀

A high-performance YouTube influencer scraper designed to collect data on 10,000+ YouTube channels across multiple categories, cities, and countries. Features automatic API key rotation, comprehensive data extraction, and efficient CSV export.

## ✨ Features

- **🔑 Auto-Rotating API Keys**: Supports up to 20 YouTube Data API v3 keys for maximum throughput
- **🌍 Global Coverage**: Scrapes influencers from 50+ cities across 15+ countries
- **🏷️ Multi-Category Support**: 50+ categories including beauty, tech, gaming, fitness, food, travel, and more
- **📊 Rich Data Extraction**: Subscriber count, view count, video count, engagement rate, category, location, and more
- **💾 Checkpoint System**: Automatic progress saving every 1000 influencers
- **⚡ Rate Limiting**: Intelligent API quota management and rate limiting
- **📝 Comprehensive Logging**: Detailed logging with file and console output
- **🔄 Error Handling**: Robust error handling with automatic retries

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `config.py` and add your YouTube Data API v3 keys:

```python
YOUTUBE_API_KEYS = [
    "AIzaSyB...",  # Your API key 1
    "AIzaSyC...",  # Your API key 2
    "AIzaSyD...",  # Your API key 3
    # ... add up to 20 keys
]
```

**💡 How to get YouTube API keys:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Repeat for multiple keys

### 3. Test the Scraper

```bash
python test_scraper.py
```

### 4. Run Mass Scraping

```bash
python mass_scraper.py
```

## 📁 Project Structure

```
mass-scrapper/
├── youtube_scraper.py      # Core scraper class with API key rotation
├── mass_scraper.py         # Main mass scraping script
├── config.py               # Configuration and API keys
├── test_scraper.py         # Test script for verification
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── output/                 # Generated CSV files (auto-created)
    ├── youtube_influencers_10000.csv
    ├── checkpoint_1000_influencers.csv
    └── checkpoint_2000_influencers.csv
```

## 🔧 Configuration

### API Key Settings

- **Number of Keys**: Supports 1-20 API keys
- **Quota Management**: Automatic rotation when quota exceeded
- **Reset Time**: Quota resets after 1 hour

### Scraping Settings

```python
SCRAPING_CONFIG = {
    'max_results_per_search': 50,  # Max results per search
    'min_subscribers': 1000,       # Minimum subscriber count
    'rate_limit_delay': 0.1,       # Delay between API calls
    'checkpoint_interval': 1000,   # Save progress every N influencers
}
```

### Output Settings

```python
OUTPUT_CONFIG = {
    'csv_encoding': 'utf-8',
    'include_timestamp': True,
    'max_description_length': 500,
}
```

## 📊 Data Fields

Each scraped influencer includes:

| Field              | Description           | Example                                |
| ------------------ | --------------------- | -------------------------------------- |
| `channel_id`       | YouTube channel ID    | `UC1234567890`                         |
| `channel_title`    | Channel name          | `Tech Guru Mumbai`                     |
| `description`      | Channel description   | `Latest tech reviews and tutorials...` |
| `subscriber_count` | Number of subscribers | `125000`                               |
| `view_count`       | Total view count      | `25000000`                             |
| `video_count`      | Number of videos      | `450`                                  |
| `published_at`     | Channel creation date | `2020-01-15T10:30:00Z`                 |
| `category`         | Content category      | `Technology & Gadgets`                 |
| `city`             | City location         | `Mumbai`                               |
| `country`          | Country location      | `India`                                |
| `niche`            | Content niche         | `tech`                                 |
| `engagement_rate`  | Calculated engagement | `5.2`                                  |
| `search_query`     | Search terms used     | `Mumbai tech`                          |
| `scraped_at`       | Scraping timestamp    | `2024-01-15T14:30:00`                  |

## 🌍 Geographic Coverage

### Countries & Cities

- **🇮🇳 India**: Mumbai, Delhi, Bangalore, Chennai, Hyderabad, Kolkata
- **🇺🇸 USA**: LA, NYC, San Francisco, Chicago, Houston, Phoenix
- **🇬🇧 UK**: London, Manchester, Birmingham, Leeds, Liverpool
- **🇫🇷 France**: Paris, Marseille, Lyon
- **🇩🇪 Germany**: Berlin, Hamburg, Munich
- **🇮🇹 Italy**: Milan, Rome
- **🇯🇵 Japan**: Tokyo, Osaka, Yokohama
- **🇦🇺 Australia**: Sydney, Melbourne, Brisbane
- **🇨🇦 Canada**: Toronto, Montreal, Vancouver

### Categories

- **Beauty & Fashion**: makeup, skincare, fashion, beauty
- **Technology**: tech, programming, gadgets, AI
- **Gaming**: gaming, esports, streaming
- **Fitness & Health**: fitness, yoga, nutrition, wellness
- **Food & Cooking**: food, cooking, baking, restaurants
- **Travel & Lifestyle**: travel, lifestyle, vlogs
- **Education**: education, tutorials, courses
- **Business & Finance**: business, finance, entrepreneurship
- **Music & Arts**: music, art, dance
- **Sports**: sports, athletics, workout
- **Automotive**: cars, bikes, automotive
- **Parenting**: parenting, family, kids
- **Science**: science, research, innovation
- **Entertainment**: comedy, entertainment, funny
- **DIY & Crafts**: diy, crafts, hacks
- **Reviews**: reviews, testing, unboxing

## ⚡ Performance

### Expected Output

- **Target**: 10,000+ influencers
- **Rate**: ~500-1000 influencers/hour (with 20 API keys)
- **Duration**: 10-20 hours for full scrape
- **Storage**: ~50-100MB CSV files

### API Quota Management

- **Quota per key**: 10,000 units/day
- **Search request**: 100 units
- **Channel request**: 1 unit
- **With 20 keys**: 200,000 units/day total

## 🛠️ Usage Examples

### Basic Usage

```python
from youtube_scraper import YouTubeInfluencerScraper

# Initialize with multiple API keys
api_keys = ["key1", "key2", "key3"]
scraper = YouTubeInfluencerScraper(api_keys)

# Search for channels
channels = scraper.search_channels("Mumbai", "tech", max_results=10)

# Get channel statistics
for channel in channels:
    stats = scraper.get_channel_statistics(channel['channelId'])
    print(f"{stats['channelTitle']}: {stats['subscriberCount']} subscribers")

scraper.close()
```

### Custom Search Configuration

```python
# Modify search configs in mass_scraper.py
custom_configs = [
    {"category": "your_category", "cities": ["Your City"]},
    # Add more custom combinations
]
```

## 🔍 Monitoring & Logs

### Log Files

- **Console**: Real-time progress updates
- **File**: `youtube_scraper.log` (detailed logging)
- **Checkpoints**: Progress saved every 1000 influencers

### Progress Tracking

```
🏷️  Processing category: tech
   Cities: Mumbai, Delhi, Bangalore, Chennai, New York, San Francisco, London, Tokyo, Berlin
🔍 Scraping tech influencers in Mumbai...
   ✅ Found 45 channels
   ✅ Added: Tech Guru Mumbai (125,000 subscribers)
   📊 Progress: 1,245/10,000 influencers collected
   🔍 Searches completed: 89
   ⏱️  Rate: 847.2 influencers/hour
   🔑 Active API keys: 18/20
```

## ⚠️ Important Notes

### Rate Limiting

- YouTube API has strict rate limits
- Each API key: 10,000 units/day
- Search requests: 100 units each
- Channel requests: 1 unit each

### Best Practices

1. **Use multiple API keys** for higher throughput
2. **Don't exceed rate limits** to avoid temporary bans
3. **Monitor quota usage** through logs
4. **Use checkpoints** for long-running scrapes
5. **Respect YouTube's terms of service**

### Legal Considerations

- This tool is for educational/research purposes
- Respect YouTube's Terms of Service
- Don't scrape data for commercial use without permission
- Be mindful of rate limits and API quotas

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**

   - Verify API keys are valid and have YouTube Data API v3 enabled
   - Check quota limits in Google Cloud Console

2. **No Results Found**

   - Try different city/category combinations
   - Check if search terms are too specific

3. **Rate Limiting**

   - Add more API keys
   - Increase delays between requests
   - Wait for quota reset (1 hour)

4. **Memory Issues**
   - Reduce batch sizes
   - Use checkpoints more frequently

### Debug Mode

Enable debug logging in `config.py`:

```python
LOGGING_CONFIG = {
    'level': 'DEBUG',  # Change from 'INFO' to 'DEBUG'
    # ... other settings
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect YouTube's Terms of Service and use responsibly.

## 🆘 Support

If you encounter issues:

1. Check the logs for error messages
2. Verify API key configuration
3. Test with the test script first
4. Check YouTube API quota status

## 🎯 Roadmap

- [ ] Database storage support (MySQL, PostgreSQL)
- [ ] Proxy rotation for IP diversity
- [ ] Advanced filtering and sorting
- [ ] Real-time monitoring dashboard
- [ ] Export to multiple formats (JSON, Excel)
- [ ] Scheduled scraping with cron jobs
- [ ] Multi-threading support
- [ ] Advanced analytics and insights

---

**Happy Scraping! 🚀**
