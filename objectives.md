## NewsWrite Bot – Objectives

### High-Level Goal

**Build a Python workflow system that automatically monitors RSS feeds, extracts images, rewrites articles with LLM, and delivers ready posts to social media bots via webhook.**

### Phase 1 – Multi-RSS Feed Monitoring

- **Objective 1**: Monitor multiple RSS feeds simultaneously.
  - Support configurable RSS feed list in `config.yaml`.
  - Easily add new feeds without code changes.
  - Handle different RSS formats (RSS 2.0, Atom, RDF) via feedparser normalization.
  - Track feed metadata (name, URL, enabled status).

- **Objective 2**: Detect new articles automatically.
  - Compare fetched articles with SQLite database.
  - Only process articles that haven't been seen before.
  - Store new articles with status 'pending' for processing.
  - Rate limiting between feed requests to be respectful.

### Phase 2 – Image Extraction & Storage

- **Objective 3**: Extract images from articles.
  - First check RSS feed for embedded images (media_content, enclosures).
  - If not found, scrape article page using BeautifulSoup.
  - Multiple selector strategies for finding featured images.
  - Filter out logos, icons, and small images (<200px).
  - Store image URLs in database.

- **Objective 4**: SQLite database for article tracking.
  - Store all processed articles with metadata.
  - Track article states: 'pending' → 'ready'.
  - Maintain processing history and logs.
  - Prevent duplicate processing.

### Phase 3 – OpenRouter LLM Integration

- **Objective 5**: Integrate OpenRouter API for rewriting.
  - Use OpenAI-compatible API client (OpenRouter supports multiple models).
  - Configurable model selection (GPT-4, Claude, Gemini, etc.).
  - Support configurable temperature and max_tokens.

- **Objective 6**: Design effective rewrite prompts.
  - Generate social media-appropriate posts (Twitter/X style).
  - Keep under 280 characters.
  - Include relevant hashtags.
  - Preserve key facts from original article.
  - Add emoji when appropriate.
  - Include link to original article.

- **Objective 7**: Ensure factual accuracy and tone control.
  - Prompts must preserve facts from original.
  - Avoid clickbait and misrepresentation.
  - Maintain professional yet engaging tone.
  - Error handling for LLM API failures.

### Phase 4 – Webhook Output System

- **Objective 8**: Deliver posts to social media bots via webhook.
  - Primary output method: POST to configured webhook URL.
  - JSON format with rewritten_text, image_url, source_url, metadata.
  - Error handling: fallback to file save if webhook fails.
  - Support batch delivery of multiple ready posts.

- **Objective 9**: Continuous workflow automation.
  - Scheduled runs at configurable intervals (default: 30 minutes).
  - Command-line option for single run (`--once` flag).
  - Log all workflow runs and errors.
  - Process articles in batches (configurable limit).

### Phase 5 – Server Deployment & Monitoring

- **Objective 10**: Deploy to PikaPods (or similar container hosting).
  - Dockerfile for containerization.
  - Environment variable configuration.
  - Persistent storage for database and logs.
  - Continuous operation without manual intervention.

- **Objective 11**: Logging and monitoring.
  - Track which articles were ingested.
  - Track which posts were generated and sent.
  - Log processing errors and webhook delivery status.
  - Store processing history in database.

### Architecture Principles

- **Modularity**: Each component (RSS, image extraction, LLM, output) is separate and testable.
- **Configuration-driven**: RSS feeds, LLM settings, and webhook URL in `config.yaml`.
- **Extensibility**: Easy to add new RSS feeds without code changes.
- **Reliability**: Error handling at each step, fallback mechanisms.
- **Separation of concerns**: This bot only processes and outputs. Social media posting handled by separate bots.

### Future Enhancements (Not in Current Scope)

- Human review mode before webhook delivery.
- Content filtering (topic-based, tone-based).
- Multiple output formats (different social platforms).
- Analytics and engagement tracking.
- Feed validation and health monitoring.
