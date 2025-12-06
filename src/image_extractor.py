"""
Image extractor for scraping featured images from article pages.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional


class ImageExtractor:
    """Extract images from article pages."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_image(self, article_url: str, rss_image: str = None) -> Optional[str]:
        """
        Extract main image from article. Returns the image URL or None if not found.
        First tries RSS image, then scrapes article page.
        """
        # If RSS feed already has image, use it
        if rss_image:
            return rss_image
        
        # Otherwise, scrape from article page
        try:
            response = requests.get(article_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple strategies to find the main image
            image_url = None
            
            # Strategy 1: Look for common image selectors
            selectors = [
                'img.article-image',
                'img.featured-image',
                'img.wp-post-image',
                'article img:first-of-type',
                '.post-content img:first-of-type',
                'main img:first-of-type',
                '.content img:first-of-type'
            ]
            
            for selector in selectors:
                img = soup.select_one(selector)
                if img:
                    image_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if image_url:
                        image_url = urljoin(article_url, image_url)
                        # Check if it's a reasonable size (not a tiny icon)
                        width = img.get('width')
                        if width:
                            try:
                                if int(width) > 200:
                                    return image_url
                            except ValueError:
                                pass
                        else:
                            # No width info, but found via selector, use it
                            return image_url
            
            # Strategy 2: Get first large image from article content
            if not image_url:
                imgs = soup.find_all('img')
                for img in imgs:
                    img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if img_url:
                        img_url = urljoin(article_url, img_url)
                        # Filter out common non-content images
                        skip_keywords = ['logo', 'icon', 'avatar', 'button', 'ad', 'banner', 'sponsor']
                        if any(skip in img_url.lower() for skip in skip_keywords):
                            continue
                        width = img.get('width')
                        if width:
                            try:
                                if int(width) > 300:
                                    return img_url
                            except ValueError:
                                pass
                        # If no width but not a skip keyword, consider it
                        if not any(skip in img.get('class', []) for skip in skip_keywords):
                            return img_url
            
            return None
            
        except Exception as e:
            print(f"  ⚠ Error extracting image from {article_url}: {e}")
            return None



