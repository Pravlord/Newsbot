"""
Output queue for generating and delivering posts to social media bots via webhook.
"""
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import requests
import os


class OutputQueue:
    """Generate output files and send to webhook for social media bots."""
    
    def __init__(self, config: Dict):
        self.output_dir = Path(config.get('directory', 'data/output'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.format = config.get('format', 'json')
        # Webhook URL from config or environment variable
        self.webhook_url = config.get('webhook_url') or os.getenv('WEBHOOK_URL', '')
        self.include_original = config.get('include_original', False)
    
    def generate_output(self, articles: List[Dict]) -> List[Dict]:
        """Generate output format for social media bots."""
        output_items = []
        
        for article in articles:
            output_item = {
                'id': article.get('id'),
                'title': article.get('title'),
                'rewritten_text': article.get('rewritten_content'),
                'image_url': article.get('image_url'),
                'source_url': article.get('article_url'),
                'feed_name': article.get('feed_name'),
                'published_date': article.get('published_date'),
                'processed_at': article.get('processed_at'),
                'ready_for_posting': True
            }
            
            if self.include_original:
                output_item['original'] = {
                    'title': article.get('title'),
                    'content': article.get('original_content')
                }
            
            output_items.append(output_item)
        
        return output_items
    
    def save_to_file(self, articles: List[Dict]) -> Path:
        """Save articles to JSON file as backup."""
        output_items = self.generate_output(articles)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"ready_posts_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_items, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(output_items)} posts to {filename}")
        return filename
    
    def send_to_webhook(self, articles: List[Dict]) -> bool:
        """Send articles to webhook (primary output method)."""
        if not self.webhook_url:
            print("⚠ No webhook URL configured. Skipping webhook delivery.")
            return False
        
        output_items = self.generate_output(articles)
        
        if not output_items:
            print("⚠ No articles to send to webhook.")
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                json=output_items,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            print(f"✓ Sent {len(output_items)} posts to webhook: {self.webhook_url}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠ Webhook error: {e}")
            # Save to file as backup
            self.save_to_file(articles)
            return False



