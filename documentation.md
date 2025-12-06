## NewsWrite Bot – Technical Documentation

### Overview

**NewsWrite Bot** is a tool that automatically pulls news from selected sources, rewrites it for social media using an LLM, and then publishes it to our social channels.  
Phase 1 focuses on **pulling and inspecting RSS feeds**; later phases will add **LLM rewriting** and **automated posting**.

### Tech Stack (initial)

- **Language**: Python 3
- **Libraries**:
  - **feedparser**: for parsing RSS feeds
  - (future) **httpx/requests**: for HTTP calls to LLM APIs and social APIs
  - (future) **schedule / cron**: for periodic runs

### Current Features (Phase 1)

- **RSS ingestion demo**
  - File: `rss_example.py`
  - Uses `feedparser` to:
    - Fetch the MarineLink RSS feed at `https://www.marinelink.com/news/rss`
    - Print basic feed metadata (title, link)
    - Print the first 10 items with title, link, published date, and a truncated summary

#### How to Run the Demo

1. **Install dependencies** (already done once via pip, but repeatable):
   - `pip install -r requirements.txt`
2. **Run the script**:
   - `python rss_example.py`

You should see the feed title and link, followed by details for the first 10 articles.

### Planned Architecture

- **Ingestion Layer**
  - Pull RSS feeds from configurable URLs.
  - Normalize articles (title, url, published date, source, summary/body).
  - Store raw and cleaned content (future: simple DB or local JSON/SQLite).

- **LLM Rewriting Layer**
  - For each selected article:
    - Build a prompt that:
      - Preserves facts and links to the original.
      - Adapts tone and length for each social platform (Twitter/X, LinkedIn, etc.).
    - Call an LLM API (e.g., OpenAI, local model) to generate:
      - Short headline
      - Main post text
      - Optional hashtags / call to action

- **Publishing Layer**
  - Integrations with platform APIs (Twitter/X, LinkedIn, etc.).
  - Queues posts for review or auto-publishing.
  - Simple configuration for:
    - Which feeds to follow
    - Posting frequency
    - Target platforms and credentials (via env vars / config file).

### Configuration (future)

- A config file (e.g., `config.yaml` or `.env`) will define:
  - RSS feed URLs (start with MarineLink, later add others).
  - LLM provider and API keys.
  - Social platforms, credentials, and posting rules.

### Security & Safety Considerations (future)

- **Credentials**:
  - Never commit API keys to version control.
  - Use environment variables or a secrets manager.
- **Content safety**:
  - Add filters for:
    - Disallowed topics
    - Tone (e.g., no sensationalism, no misrepresentation)
  - Human-in-the-loop mode before full auto-posting.

### Next Steps for Implementation

1. Wrap RSS fetching into a small reusable module (e.g., `rss_client.py`).
2. Add a simple storage layer (JSON/SQLite) for fetched articles.
3. Integrate the first LLM provider to rewrite a single article into a tweet-style post.
4. Add a command-line interface to:
   - Fetch latest articles
   - Rewrite them
   - Print or save the social-ready text.



