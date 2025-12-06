"""
SQLite database module for tracking processed articles.
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path


class ArticleStorage:
    """SQLite database for tracking processed articles."""
    
    def __init__(self, db_path: str = "data/articles.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_url TEXT UNIQUE NOT NULL,
                feed_name TEXT NOT NULL,
                title TEXT NOT NULL,
                published_date TEXT,
                image_url TEXT,
                original_content TEXT,
                rewritten_content TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                new_articles INTEGER,
                processed_articles INTEGER,
                errors TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def article_exists(self, article_url: str) -> bool:
        """Check if article has been processed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM articles WHERE article_url = ?", (article_url,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def save_article(self, article_data: Dict) -> int:
        """Save article to database. Returns article ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO articles 
            (article_url, feed_name, title, published_date, image_url, original_content, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            article_data['url'],
            article_data.get('feed_name', ''),
            article_data['title'],
            article_data.get('published', ''),
            article_data.get('image_url'),
            article_data.get('content', '') or article_data.get('summary', ''),
            'pending'
        ))
        
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return article_id
    
    def update_article_image(self, article_url: str, image_url: str):
        """Update article with extracted image URL."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE articles 
            SET image_url = ?
            WHERE article_url = ?
        """, (image_url, article_url))
        conn.commit()
        conn.close()
    
    def update_article_content(self, article_url: str, content: str, image_url: str = None):
        """Update article with scraped full content and image."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if image_url:
            cursor.execute("""
                UPDATE articles 
                SET original_content = ?, image_url = ?
                WHERE article_url = ?
            """, (content, image_url, article_url))
        else:
            cursor.execute("""
                UPDATE articles 
                SET original_content = ?
                WHERE article_url = ?
            """, (content, article_url))
        
        conn.commit()
        conn.close()
    
    def update_article_rewrite(self, article_url: str, rewritten_content: str):
        """Update article with rewritten content."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE articles 
            SET rewritten_content = ?, status = 'ready', processed_at = CURRENT_TIMESTAMP
            WHERE article_url = ?
        """, (rewritten_content, article_url))
        conn.commit()
        conn.close()
    
    def get_pending_articles(self, limit: int = 10) -> List[Dict]:
        """Get articles pending LLM processing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM articles 
            WHERE status = 'pending' 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        articles = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return articles
    
    def get_ready_articles(self, limit: int = 50) -> List[Dict]:
        """Get articles ready for social media bots."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM articles 
            WHERE status = 'ready' 
            ORDER BY processed_at DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        articles = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return articles
    
    def log_processing_run(self, new_articles: int, processed_articles: int, errors: str = None):
        """Log a workflow run."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO processing_log (new_articles, processed_articles, errors)
            VALUES (?, ?, ?)
        """, (new_articles, processed_articles, errors))
        conn.commit()
        conn.close()


