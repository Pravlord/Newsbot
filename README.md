# NewsWrite Bot

Automated workflow system that monitors RSS feeds, extracts images, rewrites articles with LLM, and delivers ready posts to social media bots via webhook.

## Architecture

**Workflow**: RSS Feeds → New Article Detection → Image Extraction → LLM Rewriting → Webhook Output

## Features

- **Multi-RSS Feed Monitoring**: Monitor multiple RSS feeds simultaneously
- **New Article Detection**: Automatically detects and processes only new articles
- **Image Extraction**: Scrapes featured images from article pages
- **LLM Rewriting**: Uses OpenRouter to rewrite articles for social media
- **Webhook Delivery**: Sends ready posts to your social media bots
- **SQLite Storage**: Tracks all processed articles to prevent duplicates
- **Easy Configuration**: Add new RSS feeds via YAML config (no code changes)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

1. Copy `.env.example` to `.env` and add your OpenRouter API key:
   ```bash
   OPENROUTER_API_KEY=your_key_here
   ```

2. Edit `config.yaml`:
   - Add/configure RSS feeds
   - Set webhook URL for your social media bots
   - Configure LLM model and settings

### 3. Run

**Single run (for testing):**
```bash
python main.py --once
```

**Continuous mode (production):**
```bash
python main.py
```

## Configuration

### RSS Feeds (`config.yaml`)

Add feeds easily - no code changes needed:

```yaml
rss_feeds:
  - name: "MarineLink"
    url: "https://www.marinelink.com/news/rss"
    enabled: true
  - name: "BBC News"
    url: "http://feeds.bbci.co.uk/news/rss.xml"
    enabled: true
```

### LLM Settings

Configure OpenRouter model and parameters:

```yaml
llm:
  model: "openai/gpt-4"  # or "anthropic/claude-3-opus", etc.
  temperature: 0.7
  max_tokens: 500
```

### Webhook Output

Set your social media bot webhook URL:

```yaml
output:
  webhook_url: "https://your-bot-server.com/webhook/newsposts"
```

## Output Format

Posts are delivered to your webhook as JSON:

```json
[
  {
    "id": 1,
    "title": "Article Title",
    "rewritten_text": "🚢 Breaking news about... #News #Tech",
    "image_url": "https://example.com/image.jpg",
    "source_url": "https://original-article.com",
    "feed_name": "MarineLink",
    "published_date": "Tue, 02 Dec 2025 12:21:28 Z",
    "processed_at": "2025-12-02 14:30:00",
    "ready_for_posting": true
  }
]
```

## Project Structure

```
newswrite-bot/
├── src/
│   ├── __init__.py
│   ├── storage.py          # SQLite database
│   ├── rss_processor.py    # RSS feed monitoring
│   ├── image_extractor.py  # Image scraping
│   ├── llm_rewriter.py     # OpenRouter LLM
│   └── output_queue.py     # Webhook delivery
├── data/
│   ├── articles.db         # SQLite database (created at runtime)
│   └── output/             # Backup JSON files
├── logs/                    # Application logs
├── config.yaml             # Configuration
├── main.py                 # Workflow orchestrator
├── requirements.txt        # Dependencies
└── Dockerfile             # For PikaPods deployment
```

## Deployment to PikaPods

1. Push code to GitHub
2. In PikaPods: Deploy from GitHub repository
3. Set environment variables:
   - `OPENROUTER_API_KEY`
   - `WEBHOOK_URL` (optional, can be in config.yaml)
4. The bot runs continuously

## How It Works

1. **RSS Monitoring**: Checks configured feeds at intervals
2. **New Article Detection**: Compares with database to find new articles
3. **Image Extraction**: Scrapes article pages for featured images
4. **LLM Rewriting**: Processes articles with OpenRouter
5. **Webhook Delivery**: Sends ready posts to your social media bots

## Requirements

- Python 3.11+
- OpenRouter API key
- Webhook endpoint for social media bots

## License

MIT



