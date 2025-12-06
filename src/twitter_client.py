"""
Twitter/X API Client for posting tweets.
Uses Twitter API v1.1 with OAuth 1.0a authentication.
"""
import os
import logging
from typing import Dict, Optional
from requests_oauthlib import OAuth1Session

logger = logging.getLogger(__name__)


class TwitterClient:
    """Post tweets to Twitter/X using OAuth 1.0a."""
    
    # Twitter API v1.1 endpoint for posting tweets
    TWEET_ENDPOINT = "https://api.twitter.com/1.1/statuses/update.json"
    
    # Twitter API v2 endpoint (alternative)
    TWEET_V2_ENDPOINT = "https://api.twitter.com/2/tweets"
    
    def __init__(self):
        """Initialize Twitter client with credentials from environment variables."""
        self.api_key = os.getenv("TWITTER_API_KEY", "")
        self.api_secret = os.getenv("TWITTER_API_SECRET", "")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET", "")
        
        self._session: Optional[OAuth1Session] = None
        
        if self.is_configured():
            self._session = OAuth1Session(
                client_key=self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_secret
            )
            logger.info("Twitter client initialized with OAuth credentials")
        else:
            logger.warning("Twitter client not configured - missing credentials")
    
    def is_configured(self) -> bool:
        """Check if all required credentials are present."""
        return all([
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_secret
        ])
    
    def post_tweet(self, text: str) -> Dict:
        """
        Post a tweet to Twitter.
        
        Args:
            text: The tweet text (max 280 characters)
        
        Returns:
            dict with keys:
                - ok: bool indicating success
                - tweet_id: str tweet ID if successful
                - error: str error message if failed
        """
        if not self._session:
            return {"ok": False, "error": "Twitter client not configured"}
        
        # Truncate text if too long (Twitter limit is 280 chars)
        # URLs are shortened to 23 chars by Twitter, so we have some buffer
        if len(text) > 280:
            logger.warning(f"Tweet text too long ({len(text)} chars), truncating")
            text = text[:277] + "..."
        
        try:
            # Try v2 API first (newer, recommended)
            response = self._post_tweet_v2(text)
            if response.get("ok"):
                return response
            
            # Fall back to v1.1 if v2 fails
            logger.info("v2 API failed, trying v1.1")
            return self._post_tweet_v1(text)
            
        except Exception as e:
            logger.error(f"Twitter post error: {e}")
            return {"ok": False, "error": str(e)}
    
    def _post_tweet_v2(self, text: str) -> Dict:
        """Post using Twitter API v2."""
        try:
            response = self._session.post(
                self.TWEET_V2_ENDPOINT,
                json={"text": text}
            )
            
            if response.status_code == 201:
                data = response.json()
                tweet_id = data.get("data", {}).get("id")
                return {"ok": True, "tweet_id": tweet_id}
            else:
                error_data = response.json()
                error_msg = error_data.get("detail") or error_data.get("title") or str(error_data)
                return {"ok": False, "error": f"v2 API error ({response.status_code}): {error_msg}"}
                
        except Exception as e:
            return {"ok": False, "error": f"v2 API exception: {e}"}
    
    def _post_tweet_v1(self, text: str) -> Dict:
        """Post using Twitter API v1.1."""
        try:
            response = self._session.post(
                self.TWEET_ENDPOINT,
                data={"status": text}
            )
            
            if response.status_code == 200:
                data = response.json()
                tweet_id = str(data.get("id"))
                return {"ok": True, "tweet_id": tweet_id}
            else:
                error_data = response.json()
                errors = error_data.get("errors", [])
                error_msg = errors[0].get("message") if errors else str(error_data)
                return {"ok": False, "error": f"v1.1 API error ({response.status_code}): {error_msg}"}
                
        except Exception as e:
            return {"ok": False, "error": f"v1.1 API exception: {e}"}

