"""
Article scraper for extracting full content and images from article pages.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional, Dict, Tuple


class ArticleScraper:
    """Scrape full content and images from article pages."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self._cached_soup = None
        self._cached_url = None
    
    def scrape_article(self, article_url: str, rss_image: str = None) -> Dict[str, Optional[str]]:
        """
        Scrape article page for full content and image.
        Returns dict with 'content' and 'image_url' keys.
        """
        result = {
            'content': None,
            'image_url': None
        }
        
        try:
            response = requests.get(article_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                                 'aside', 'iframe', 'noscript', 'form']):
                element.decompose()
            
            # Extract full content
            result['content'] = self._extract_content(soup)
            
            # Always try to get high-res image from page (og:image, twitter:image)
            result['image_url'] = self._extract_image(soup, article_url)
            
            # Fall back to RSS image only if we couldn't find one on the page
            # BUT skip RSS image if it looks like a thumbnail (contains size indicators)
            if not result['image_url']:
                if rss_image and not self._is_thumbnail_url(rss_image):
                    result['image_url'] = rss_image
                elif rss_image:
                    # RSS image is a thumbnail, still use it as last resort
                    result['image_url'] = rss_image
            
            return result
            
        except Exception as e:
            print(f"  ⚠ Error scraping {article_url}: {e}")
            return result
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract full article content from page."""
        
        # Try multiple content selectors (most specific first)
        content_selectors = [
            'article .article-content',
            'article .post-content',
            'article .entry-content',
            '.article-body',
            '.post-body',
            '.story-content',
            '.news-content',
            'article',
            '.post-content',
            '.entry-content',
            'main article',
            'main .content',
            '.content-area',
            'main'
        ]
        
        content = None
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Get text, preserving paragraph structure
                paragraphs = content_elem.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                else:
                    content = content_elem.get_text(separator='\n', strip=True)
                
                # Check if we got meaningful content (at least 200 chars)
                if content and len(content) > 200:
                    break
        
        # Clean up content
        if content:
            # Remove excessive whitespace
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n\n'.join(lines)
        
        return content
    
    def _is_thumbnail_url(self, url: str) -> bool:
        """Check if URL looks like a thumbnail/low-res version."""
        if not url:
            return False
        url_lower = url.lower()
        # Common thumbnail indicators in URLs
        thumbnail_indicators = [
            '/w150/', '/w200/', '/w300/',  # width-based paths
            '/h150/', '/h200/', '/h300/',  # height-based paths
            '-150x', '-200x', '-300x',     # WordPress-style dimensions
            '_thumb', '_small', '_tiny',
            '/thumb/', '/thumbs/',
            '/small/', '/preview/',
            'resize=', 'width=150', 'width=200',
        ]
        return any(indicator in url_lower for indicator in thumbnail_indicators)
    
    def _upgrade_thumbnail_url(self, url: str) -> str:
        """Try to upgrade a thumbnail URL to full resolution."""
        if not url:
            return url
        
        # MarineLink specific: replace /w150/ with larger size or remove
        import re
        # Try to get original by removing size indicator
        upgraded = re.sub(r'/w\d+/', '/', url)
        if upgraded != url:
            return upgraded
        
        # WordPress: remove dimension suffix like -150x150
        upgraded = re.sub(r'-\d+x\d+\.', '.', url)
        return upgraded
    
    def _extract_image(self, soup: BeautifulSoup, article_url: str) -> Optional[str]:
        """Extract main image from article page."""
        
        # Strategy 1: Look for Open Graph or Twitter Card image (usually full resolution)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = urljoin(article_url, og_image['content'])
            # If og:image is also a thumbnail, try to upgrade it
            if self._is_thumbnail_url(img_url):
                img_url = self._upgrade_thumbnail_url(img_url)
            return img_url
        
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            img_url = urljoin(article_url, twitter_image['content'])
            if self._is_thumbnail_url(img_url):
                img_url = self._upgrade_thumbnail_url(img_url)
            return img_url
        
        # Strategy 2: Look for common image selectors
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
                    width = img.get('width')
                    if width:
                        try:
                            if int(width) > 200:
                                return image_url
                        except ValueError:
                            pass
                    else:
                        return image_url
        
        # Strategy 3: Get first large image
        imgs = soup.find_all('img')
        for img in imgs:
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if img_url:
                img_url = urljoin(article_url, img_url)
                # Filter out common non-content images
                skip_keywords = ['logo', 'icon', 'avatar', 'button', 'ad', 'banner', 'sponsor', 'pixel']
                if any(skip in img_url.lower() for skip in skip_keywords):
                    continue
                width = img.get('width')
                if width:
                    try:
                        if int(width) > 300:
                            return img_url
                    except ValueError:
                        pass
                else:
                    # No width but not a skip keyword
                    return img_url
        
        return None
    
    # Keep old method for backwards compatibility
    def extract_image(self, article_url: str, rss_image: str = None) -> Optional[str]:
        """Extract main image from article (backwards compatible)."""
        result = self.scrape_article(article_url, rss_image)
        return result.get('image_url')


