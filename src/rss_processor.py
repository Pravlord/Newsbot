"""
RSS feed processor for monitoring multiple feeds and detecting new articles.
"""
import feedparser
from typing import List, Dict, Optional
import time


class RSSProcessor:
    """Process multiple RSS feeds and extract new articles."""
    
    def __init__(self, feeds_config: List[Dict]):
        self.feeds = [f for f in feeds_config if f.get('enabled', True)]
    
    def fetch_feed(self, feed_config: Dict) -> List[Dict]:
        """Fetch and parse a single RSS feed."""
        try:
            feed = feedparser.parse(feed_config['url'])
            
            articles = []
            for entry in feed.entries:
                article = {
                    'feed_name': feed_config['name'],
                    'title': entry.title,
                    'url': entry.link,
                    'published': getattr(entry, 'published', ''),
                    'summary': getattr(entry, 'summary', ''),
                    'content': self._extract_content(entry),
                    'rss_image': self._extract_rss_image(entry)
                }
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"  ⚠ Error fetching feed {feed_config['name']}: {e}")
            return []
    
    def _extract_content(self, entry) -> str:
        """Extract full content from RSS entry."""
        # Try content:encoded first (full article)
        if hasattr(entry, 'content') and entry.content:
            return entry.content[0].get('value', '')
        # Fallback to summary
        return getattr(entry, 'summary', '')
    
    def _extract_rss_image(self, entry) -> str:
        """Extract image URL from RSS entry if available."""
        # Check media_content (Atom/Media RSS)
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('type', '').startswith('image/'):
                    return media.get('url', '')
        
        # Check enclosures (RSS 2.0)
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc.get('href', '')
        
        # Check image tag
        if hasattr(entry, 'image') and entry.image:
            if isinstance(entry.image, dict):
                return entry.image.get('href', '')
            return str(entry.image)
        
        return ''
    
    def check_topmost_article(self, storage) -> Optional[Dict]:
        """
        Check only the topmost (newest) article from feeds.
        Returns the article if it's new, None if already processed.
        This is more efficient than checking all articles.
        """
        for feed_config in self.feeds:
            print(f"📡 Checking feed: {feed_config['name']}")
            articles = self.fetch_feed(feed_config)
            
            if articles:
                topmost = articles[0]  # First article = newest
                
                if not storage.article_exists(topmost['url']):
                    print(f"  ✓ New article found: {topmost['title'][:50]}...")
                    return topmost
                else:
                    print(f"  ✓ Topmost article already processed. No new content.")
                    return None
            else:
                print(f"  ⚠ No articles in feed")
        
        return None
    
    def get_new_articles(self, storage, max_per_feed: int = 10) -> List[Dict]:
        """Get new articles from all feeds (legacy method)."""
        all_new_articles = []
        
        for feed_config in self.feeds:
            print(f"📡 Checking feed: {feed_config['name']}")
            articles = self.fetch_feed(feed_config)
            
            new_count = 0
            for article in articles[:max_per_feed]:
                if not storage.article_exists(article['url']):
                    all_new_articles.append(article)
                    storage.save_article(article)
                    new_count += 1
            
            print(f"  ✓ Found {new_count} new articles")
            time.sleep(1)  # Be polite to servers
        
        return all_new_articles


