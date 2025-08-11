#!/usr/bin/env python3
"""
YouTube Influencer Scraper with API Key Rotation
Comprehensive channel data extraction with rate limiting and error handling
"""

import requests
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging

class YouTubeInfluencerScraper:
    def __init__(self, api_keys: List[str]):
        """
        Initialize scraper with multiple API keys for rotation
        
        Args:
            api_keys: List of YouTube Data API v3 keys
        """
        self.api_keys = api_keys
        self.current_key_index = 0
        self.key_usage = {key: {'requests': 0, 'quota_exceeded': False, 'last_reset': datetime.now()} for key in api_keys}
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Initialized scraper with {len(api_keys)} API keys")

    def _get_next_available_key(self) -> Optional[str]:
        """Get next available API key with quota"""
        attempts = 0
        while attempts < len(self.api_keys):
            key = self.api_keys[self.current_key_index]
            key_info = self.key_usage[key]
            
            # Check if quota exceeded and reset time has passed
            if key_info['quota_exceeded']:
                time_since_reset = datetime.now() - key_info['last_reset']
                if time_since_reset > timedelta(hours=1):  # Reset after 1 hour
                    key_info['quota_exceeded'] = False
                    key_info['requests'] = 0
                    key_info['last_reset'] = datetime.now()
                    self.logger.info(f"Reset quota for API key {self.current_key_index + 1}")
            
            if not key_info['quota_exceeded']:
                return key
            
            # Move to next key
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            attempts += 1
        
        self.logger.error("All API keys have exceeded quota")
        return None

    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API request with automatic key rotation and error handling"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            api_key = self._get_next_available_key()
            if not api_key:
                return None
            
            params['key'] = api_key
            
            try:
                response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Update key usage
                    self.key_usage[api_key]['requests'] += 1
                    
                    # Check for quota exceeded
                    if 'error' in data and data['error'].get('code') == 403:
                        error_message = data['error'].get('message', '')
                        if 'quota' in error_message.lower() or 'quota exceeded' in error_message.lower():
                            self.key_usage[api_key]['quota_exceeded'] = True
                            self.logger.warning(f"API key {self.current_key_index + 1} quota exceeded")
                            retry_count += 1
                            continue
                    
                    return data
                
                elif response.status_code == 403:
                    # Quota exceeded or forbidden
                    self.key_usage[api_key]['quota_exceeded'] = True
                    self.logger.warning(f"API key {self.current_key_index + 1} quota exceeded (403)")
                    retry_count += 1
                    continue
                
                else:
                    self.logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    retry_count += 1
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error: {str(e)}")
                retry_count += 1
                time.sleep(2 ** retry_count)
            
            # Move to next key for retry
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        
        self.logger.error(f"Failed to make API request after {max_retries} retries")
        return None

    def search_channels(self, city: str, category: str, max_results: int = 50) -> List[Dict[str, str]]:
        """
        Search for YouTube channels by city and category
        
        Args:
            city: City name for location-based search
            category: Category/topic for search
            max_results: Maximum number of results to return
            
        Returns:
            List of channel information dictionaries
        """
        search_query = f"{city} {category}"
        self.logger.info(f"Searching for channels: {search_query}")
        
        params = {
            'part': 'snippet',
            'q': search_query,
            'type': 'channel',
            'maxResults': min(max_results, 50),  # API limit is 50
            'order': 'relevance',
            'publishedAfter': '2010-01-01T00:00:00Z'  # Channels created after 2010
        }
        
        channels = []
        next_page_token = None
        
        while len(channels) < max_results:
            if next_page_token:
                params['pageToken'] = next_page_token
            
            data = self._make_api_request('search', params)
            if not data:
                break
            
            items = data.get('items', [])
            if not items:
                break
            
            for item in items:
                if len(channels) >= max_results:
                    break
                
                channel_info = {
                    'channelId': item['snippet']['channelId'],
                    'channelTitle': item['snippet']['channelTitle'],
                    'description': item['snippet'].get('description', ''),
                    'publishedAt': item['snippet'].get('publishedAt', ''),
                    'searchQuery': search_query
                }
                channels.append(channel_info)
            
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
            
            # Rate limiting
            time.sleep(0.1)
        
        self.logger.info(f"Found {len(channels)} channels for {search_query}")
        return channels

    def get_channel_statistics(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed statistics for a specific channel
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Dictionary containing channel statistics and details
        """
        self.logger.debug(f"Getting statistics for channel: {channel_id}")
        
        # Get channel details
        params = {
            'part': 'snippet,statistics,brandingSettings',
            'id': channel_id
        }
        
        data = self._make_api_request('channels', params)
        if not data or 'items' not in data or not data['items']:
            return None
        
        channel = data['items'][0]
        snippet = channel.get('snippet', {})
        statistics = channel.get('statistics', {})
        branding = channel.get('brandingSettings', {})
        
        # Extract country from description or branding
        country = self._extract_country_from_description(snippet.get('description', ''))
        
        # Get category from description
        category = self._categorize_channel(snippet.get('description', ''), snippet.get('title', ''))
        
        channel_stats = {
            'channelId': channel_id,
            'channelTitle': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'publishedAt': snippet.get('publishedAt', ''),
            'country': country,
            'category': category,
            'subscriberCount': int(statistics.get('subscriberCount', 0)),
            'viewCount': int(statistics.get('viewCount', 0)),
            'videoCount': int(statistics.get('videoCount', 0)),
            'hiddenSubscriberCount': statistics.get('hiddenSubscriberCount', False),
            'customUrl': snippet.get('customUrl', ''),
            'defaultLanguage': snippet.get('defaultLanguage', ''),
            'defaultTab': snippet.get('defaultTab', ''),
            'keywords': snippet.get('keywords', ''),
            'topicCategories': snippet.get('topicCategories', []),
            'topicIds': snippet.get('topicIds', []),
            'thumbnails': snippet.get('thumbnails', {}),
            'banner': branding.get('image', {}).get('bannerExternalUrl', ''),
            'scrapedAt': datetime.now().isoformat()
        }
        
        return channel_stats

    def _extract_country_from_description(self, description: str) -> str:
        """Extract country information from channel description"""
        description_lower = description.lower()
        
        # Common country indicators
        country_indicators = {
            'india': ['india', 'indian', 'mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad', 'kolkata'],
            'usa': ['usa', 'united states', 'american', 'new york', 'los angeles', 'chicago', 'san francisco'],
            'uk': ['uk', 'united kingdom', 'british', 'london', 'manchester', 'birmingham'],
            'canada': ['canada', 'canadian', 'toronto', 'montreal', 'vancouver'],
            'australia': ['australia', 'australian', 'sydney', 'melbourne', 'brisbane'],
            'germany': ['germany', 'german', 'berlin', 'hamburg', 'munich'],
            'france': ['france', 'french', 'paris', 'marseille', 'lyon'],
            'japan': ['japan', 'japanese', 'tokyo', 'osaka', 'yokohama'],
            'south korea': ['korea', 'korean', 'seoul', 'busan', 'daegu'],
            'brazil': ['brazil', 'brazilian', 'sao paulo', 'rio de janeiro', 'brasilia']
        }
        
        for country, indicators in country_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return country
        
        return 'Unknown'

    def _categorize_channel(self, description: str, title: str) -> str:
        """Categorize channel based on description and title"""
        text = f"{title} {description}".lower()
        
        categories = {
            'Beauty & Cosmetics': ['beauty', 'makeup', 'cosmetics', 'skincare', 'hair', 'fashion'],
            'Technology & Gadgets': ['tech', 'technology', 'gadgets', 'programming', 'coding', 'software', 'ai', 'artificial intelligence'],
            'Gaming & Esports': ['gaming', 'game', 'esports', 'streaming', 'gamer', 'playthrough'],
            'Fitness & Health': ['fitness', 'health', 'workout', 'exercise', 'yoga', 'nutrition', 'wellness'],
            'Food & Cooking': ['food', 'cooking', 'recipe', 'baking', 'kitchen', 'chef', 'restaurant'],
            'Travel & Lifestyle': ['travel', 'lifestyle', 'vlog', 'adventure', 'explore', 'trip'],
            'Education & Learning': ['education', 'learning', 'tutorial', 'course', 'study', 'academic'],
            'Business & Finance': ['business', 'finance', 'entrepreneur', 'startup', 'investment', 'money'],
            'Music & Arts': ['music', 'art', 'dance', 'creative', 'artist', 'musician'],
            'Sports & Athletics': ['sports', 'athletics', 'fitness', 'workout', 'training', 'coach'],
            'Automotive & Cars': ['automotive', 'cars', 'vehicles', 'driving', 'car review', 'auto'],
            'Parenting & Family': ['parenting', 'family', 'kids', 'children', 'mom', 'dad', 'baby'],
            'Science & Technology': ['science', 'research', 'innovation', 'discovery', 'experiment'],
            'Entertainment & Comedy': ['comedy', 'entertainment', 'funny', 'humor', 'jokes', 'skits'],
            'DIY & Crafts': ['diy', 'crafts', 'hacks', 'tutorial', 'how to', 'make'],
            'Reviews & Testing': ['review', 'testing', 'unboxing', 'comparison', 'test', 'evaluate']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'Other'

    def get_api_key_status(self) -> Dict[str, Any]:
        """Get current status of all API keys"""
        status = {
            'total_keys': len(self.api_keys),
            'current_key_index': self.current_key_index,
            'keys_status': {}
        }
        
        for i, key in enumerate(self.api_keys):
            key_info = self.key_usage[key]
            status['keys_status'][f'key_{i+1}'] = {
                'requests': key_info['requests'],
                'quota_exceeded': key_info['quota_exceeded'],
                'last_reset': key_info['last_reset'].isoformat(),
                'is_current': i == self.current_key_index
            }
        
        return status

    def reset_api_key_quotas(self):
        """Reset all API key quotas (useful for testing)"""
        for key in self.api_keys:
            self.key_usage[key]['quota_exceeded'] = False
            self.key_usage[key]['requests'] = 0
            self.key_usage[key]['last_reset'] = datetime.now()
        
        self.logger.info("Reset all API key quotas")

    def close(self):
        """Clean up resources"""
        self.session.close()
        self.logger.info("Scraper session closed") 