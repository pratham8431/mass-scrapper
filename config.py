#!/usr/bin/env python3
"""
Configuration file for YouTube Mass Scraper
Contains API keys and other configuration settings
"""

# YouTube Data API v3 Keys (8 keys for rotation - more to be added)
YOUTUBE_API_KEYS = [
    "AIzaSyBfREMaYjzB4AhcK2fBB71Cvaus_Bdk_fI",
    "AIzaSyBIwv_WRhG8m3W7eHuw8P7AzlE7-ae-GjU",
    "AIzaSyBCholoklJbcx9IAgi5I5LcMwpSJzFK6f8",
    "AIzaSyBBbstfgCmrKOLdwnXzbGHItLWr0LgRIpg",
    "AIzaSyAj9FMuwvX1hkoEgXe7teB1Oc_rfOx4hns",
    "AIzaSyCIhkWEOERFmckDU7LPqEsgZ-lR3cS2IEQ",
    "AIzaSyCbWxVPqv7TndHu0X7X4ilQ9lA3J9sqW3g",
    "AIzaSyA81Goc4p4CqAgNqkVi5tKietF2NQ1I6IY"
]

# Scraping Configuration
SCRAPING_CONFIG = {
    'max_results_per_search': 50,  # Maximum results per search (API limit)
    'min_subscribers': 1000,       # Minimum subscriber count to include
    'rate_limit_delay': 0.1,       # Delay between API calls (seconds)
    'checkpoint_interval': 100,    # Save checkpoint every N influencers (reduced from 1000)
    'emergency_save_interval': 50, # Emergency save every N influencers
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

# Database Configuration (if using database storage)
DATABASE_CONFIG = {
    'use_database': False,
    'db_type': 'sqlite',  # sqlite, mysql, postgresql
    'db_host': 'localhost',
    'db_port': 3306,
    'db_name': 'youtube_influencers',
    'db_user': 'username',
    'db_password': 'password',
}

# Proxy Configuration (if using proxies)
PROXY_CONFIG = {
    'use_proxies': False,
    'proxy_list': [],
    'proxy_rotation': False,
    'proxy_auth': None,
}

# Error Handling Configuration
ERROR_CONFIG = {
    'continue_on_error': True,
    'log_errors': True,
    'save_failed_channels': True,
    'max_consecutive_errors': 10,
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'max_concurrent_requests': 1,  # YouTube API doesn't support concurrent requests well
    'connection_timeout': 30,
    'read_timeout': 30,
    'use_session_pooling': True,
} 