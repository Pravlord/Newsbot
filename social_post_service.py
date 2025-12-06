"""
Social Media Posting Service
Receives NewsWrite webhook payloads and posts to Twitter/X and Facebook.
"""
import os
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from src.twitter_client import TwitterClient
from src.facebook_client import FacebookClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Social Media Posting Service",
    description="Receives NewsWrite articles and posts to Twitter/X and Facebook",
    version="1.0.0"
)


# --- Request/Response Models ---

class PostItem(BaseModel):
    """Single article item from NewsWrite webhook.

    Note: `id` comes from the database and is an integer in the existing JSON,
    so we accept both int and str here to avoid 422s on valid payloads.
    """
    id: Optional[int | str] = None
    title: Optional[str] = None
    rewritten_text: str
    image_url: Optional[str] = None
    source_url: str
    feed_name: Optional[str] = None
    published_date: Optional[str] = None
    processed_at: Optional[str] = None
    ready_for_posting: Optional[bool] = True


class PlatformResult(BaseModel):
    """Result from posting to a single platform."""
    ok: bool
    post_id: Optional[str] = None
    error: Optional[str] = None


class PostResult(BaseModel):
    """Result for a single item posted to all platforms."""
    # Can be int or str depending on how the DB generated it
    id: Optional[int | str] = None
    title: Optional[str] = None
    twitter: Optional[PlatformResult] = None
    facebook: Optional[PlatformResult] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    twitter_configured: bool
    facebook_configured: bool


# --- Initialize Clients ---

twitter_client = TwitterClient()
facebook_client = FacebookClient()


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the service is running and which platforms are configured."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        twitter_configured=twitter_client.is_configured(),
        facebook_configured=facebook_client.is_configured()
    )


@app.post("/posts", response_model=List[PostResult])
async def receive_posts(items: List[PostItem]):
    """
    Receive articles from NewsWrite and post to configured social platforms.
    
    Expects a JSON array of items with at minimum:
    - rewritten_text: The text to post
    - source_url: Link to the original article
    
    Optional fields:
    - image_url: Image to attach (if platform supports it)
    - id, title: For tracking/logging purposes
    """
    if not items:
        raise HTTPException(status_code=400, detail="Empty items list")
    
    logger.info(f"Received {len(items)} items to post")
    
    results = []
    
    for item in items:
        logger.info(f"Processing item: {item.title or item.id or 'untitled'}")
        
        # Build the post text: rewritten content + source link
        post_text = f"{item.rewritten_text} {item.source_url}"
        
        result = PostResult(
            id=item.id,
            title=item.title
        )
        
        # Post to Twitter if configured
        if twitter_client.is_configured():
            twitter_result = twitter_client.post_tweet(post_text)
            result.twitter = PlatformResult(
                ok=twitter_result.get("ok", False),
                post_id=twitter_result.get("tweet_id"),
                error=twitter_result.get("error")
            )
            if result.twitter.ok:
                logger.info(f"  Twitter: Posted successfully (ID: {result.twitter.post_id})")
            else:
                logger.warning(f"  Twitter: Failed - {result.twitter.error}")
        else:
            logger.info("  Twitter: Not configured, skipping")
        
        # Post to Facebook if configured
        if facebook_client.is_configured():
            facebook_result = facebook_client.post_to_page(
                message=item.rewritten_text,
                link=item.source_url,
                image_url=item.image_url
            )
            result.facebook = PlatformResult(
                ok=facebook_result.get("ok", False),
                post_id=facebook_result.get("post_id"),
                error=facebook_result.get("error")
            )
            if result.facebook.ok:
                logger.info(f"  Facebook: Posted successfully (ID: {result.facebook.post_id})")
            else:
                logger.warning(f"  Facebook: Failed - {result.facebook.error}")
        else:
            logger.info("  Facebook: Not configured, skipping")
        
        results.append(result)
    
    logger.info(f"Finished processing {len(items)} items")
    return results


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SOCIAL_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

