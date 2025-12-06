"""
NewsWrite Bot - Main Workflow Orchestrator
Monitors RSS feeds, extracts images and content, rewrites with LLM, and outputs to webhook.
"""
import yaml
import schedule
import time
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.storage import ArticleStorage
from src.rss_processor import RSSProcessor
from src.article_scraper import ArticleScraper
from src.llm_rewriter import LLMRewriter
from src.output_queue import OutputQueue


# Load environment variables
load_dotenv()


class NewsWriteBot:
    """Main workflow orchestrator."""
    
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.storage = ArticleStorage()
        self.rss_processor = RSSProcessor(self.config['rss_feeds'])
        self.article_scraper = ArticleScraper()
        self.llm_rewriter = LLMRewriter(self.config['llm'])
        self.output_queue = OutputQueue(self.config['output'])
        
        self.check_interval = self.config['processing']['check_interval_minutes']
    
    def run_workflow(self):
        """
        Execute the workflow:
        1. Check topmost article in RSS feed
        2. If already processed -> exit early (no new content)
        3. If new -> scrape content + image, rewrite with LLM, send to webhook
        """
        print("="*70)
        print("🚀 NewsWrite Bot - Starting Workflow")
        print("="*70)
        print()
        
        errors = []
        new_count = 0
        processed_count = 0
        
        try:
            # Step 1: Check topmost article
            print("📡 Step 1: Checking for new articles...")
            article = self.rss_processor.check_topmost_article(self.storage)
            
            # Early exit if no new content
            if not article:
                print("\n" + "="*70)
                print("✅ No new content. Workflow complete.")
                print("="*70 + "\n")
                self.storage.log_processing_run(0, 0, None)
                return
            
            # Save article to database
            self.storage.save_article(article)
            new_count = 1
            print()
            
            # Step 2: Scrape full content and image
            print("📄 Step 2: Scraping full article content and image...")
            try:
                scraped = self.article_scraper.scrape_article(
                    article['url'],
                    article.get('rss_image', '')
                )
                
                if scraped.get('content'):
                    print(f"  ✓ Scraped {len(scraped['content'])} characters of content")
                else:
                    print(f"  ⚠ Could not scrape full content, using RSS summary")
                    scraped['content'] = article.get('content', '') or article.get('summary', '')
                
                if scraped.get('image_url'):
                    print(f"  ✓ Image found: {scraped['image_url'][:60]}...")
                else:
                    print(f"  ⚠ No image found")
                
                # Update database with scraped content
                self.storage.update_article_content(
                    article['url'],
                    scraped.get('content', ''),
                    scraped.get('image_url')
                )
                
            except Exception as e:
                errors.append(f"Scraping error: {e}")
                print(f"  ⚠ Scraping error: {e}")
            
            print()
            
            # Step 3: Rewrite with LLM
            print("🤖 Step 3: Rewriting article with LLM...")
            pending = self.storage.get_pending_articles(limit=1)
            
            if pending:
                article_data = pending[0]
                print(f"  Processing: {article_data['title'][:50]}...")
                
                try:
                    rewritten = self.llm_rewriter.rewrite_article(article_data)
                    if rewritten:
                        self.storage.update_article_rewrite(article_data['article_url'], rewritten)
                        processed_count = 1
                        print("  ✓ Rewritten successfully")
                        print(f"  Preview: {rewritten[:100]}...")
                    else:
                        errors.append(f"Failed to rewrite: {article_data['title']}")
                        print("  ⚠ Failed to rewrite")
                except Exception as e:
                    errors.append(f"LLM error: {e}")
                    print(f"  ⚠ LLM error: {e}")
            
            print()
            
            # Step 4: Output to webhook (only the newest article)
            print("📤 Step 4: Sending to social media bots...")
            ready_articles = self.storage.get_ready_articles(limit=1)  # Only newest
            
            if ready_articles:
                # Send to webhook
                success = self.output_queue.send_to_webhook(ready_articles)
                
                # If webhook fails or not configured, save to file
                if not success:
                    self.output_queue.save_to_file(ready_articles)
            else:
                print("  ⚠ No ready articles to output")
            
            print()
            
        except Exception as e:
            errors.append(f"Workflow error: {e}")
            print(f"⚠ Workflow error: {e}\n")
        
        # Log the run
        error_str = "; ".join(errors) if errors else None
        self.storage.log_processing_run(new_count, processed_count, error_str)
        
        print("="*70)
        print("✅ Workflow Complete")
        print(f"   New articles: {new_count}")
        print(f"   Processed: {processed_count}")
        if errors:
            print(f"   Errors: {len(errors)}")
        print("="*70)
        print()
    
    def run_continuously(self):
        """Run workflow on schedule."""
        # Run immediately
        self.run_workflow()
        
        # Schedule recurring runs
        schedule.every(self.check_interval).minutes.do(self.run_workflow)
        
        print(f"⏰ Scheduled to run every {self.check_interval} minutes")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n👋 Stopping NewsWrite Bot")


def main():
    """Main entry point."""
    bot = NewsWriteBot()
    
    # Run once or continuously
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        bot.run_workflow()
    else:
        bot.run_continuously()


if __name__ == "__main__":
    main()
