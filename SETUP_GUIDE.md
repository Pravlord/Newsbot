# NewsWrite Bot - Step-by-Step Setup Guide

## ✅ Step 1: Install Dependencies - COMPLETE!

All required Python packages have been installed successfully:
- feedparser ✓
- requests ✓
- beautifulsoup4 ✓
- lxml ✓
- pyyaml ✓
- openai ✓
- schedule ✓
- python-dotenv ✓

## 📝 Step 2: Create .env File (Next Step)

You need to create a `.env` file in this folder with your OpenRouter API key.

**Option 1: Manual (Recommended for beginners)**
1. In this folder, create a new text file
2. Name it exactly: `.env` (including the dot at the beginning)
3. Put this inside:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```
4. Replace `your_key_here` with your actual OpenRouter API key

**Option 2: I can create it for you**
Just let me know when you have your OpenRouter API key ready!

**Note:** The bot will still work without the API key - it just won't rewrite articles with LLM. You can test RSS feeds and image extraction first!

## ⚙️ Step 3: Check config.yaml

Open `config.yaml` - it should already be set up with:
- MarineLink RSS feed (enabled)
- BBC News RSS feed (disabled - you can enable it later)

You can add more RSS feeds here anytime - just add new entries like:
```yaml
  - name: "Your Feed Name"
    url: "https://example.com/rss"
    enabled: true
```

## 🧪 Step 4: Test Run

Once you've created the `.env` file (or even without it), you can test:

```bash
python main.py --once
```

This will:
- Fetch RSS feeds
- Detect new articles
- Extract images
- Try to rewrite with LLM (if API key is set)
- Save output to `data/output/` folder

## 📊 What Happens

1. **First Run**: Creates `data/articles.db` (SQLite database) to track articles
2. **Finds New Articles**: Compares RSS feeds with database
3. **Extracts Images**: Scrapes article pages for images
4. **Rewrites**: Uses OpenRouter LLM to create social media posts
5. **Outputs**: Saves JSON files to `data/output/` (since webhook isn't configured yet)

## 🔗 Getting OpenRouter API Key

1. Go to: https://openrouter.ai/
2. Sign up / Log in
3. Go to Keys section
4. Create a new API key
5. Copy it to your `.env` file

## 📱 Step 5: Social Media Posting Service (Optional)

The bot can automatically post articles to Twitter/X and Facebook using the included social posting service.

### 5.1 Install Additional Dependencies

```bash
pip install -r requirements.txt
```

This adds FastAPI, uvicorn, and OAuth libraries needed for the social service.

### 5.2 Configure Twitter/X Credentials

1. Go to: https://developer.twitter.com/
2. Create a new app (or use existing one)
3. Go to "Keys and tokens" section
4. Generate API Key, API Secret, Access Token, and Access Token Secret
5. Add to your `.env` file:

```
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_token_secret
```

### 5.3 Configure Facebook Credentials

1. Go to: https://developers.facebook.com/
2. Create a new app (or use existing one)
3. Add the "Pages" product to your app
4. Generate a Page Access Token with `pages_manage_posts` permission
5. Add to your `.env` file:

```
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token
```

**Tip**: Use the Graph API Explorer to generate and test tokens: https://developers.facebook.com/tools/explorer/

### 5.4 Run the Social Posting Service

In a separate terminal, start the service:

```bash
uvicorn social_post_service:app --port 8000
```

Or run directly:

```bash
python social_post_service.py
```

The service runs at `http://localhost:8000`. You can check the status at `http://localhost:8000/health`.

### 5.5 Test the Full Pipeline

With the social service running:

```bash
python main.py --once
```

Articles will now be sent to the social posting service, which will post them to any configured platforms.

### Example: Test Manually with curl

```bash
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '[{"rewritten_text": "Test post from NewsWrite", "source_url": "https://example.com/article"}]'
```

## ❓ Need Help?

Just ask! We can go through each step together.


