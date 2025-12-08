"""
Facebook Graph API Client for posting to Facebook Pages.
"""
import os
import logging
from typing import Dict, Optional
import requests

logger = logging.getLogger(__name__)


class FacebookClient:
    """Post to a Facebook Page using the Graph API."""
    
    GRAPH_API_VERSION = "v18.0"
    GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
    
    def __init__(self):
        """Initialize Facebook client with credentials from environment variables."""
        self.page_id = os.getenv("FACEBOOK_PAGE_ID", "")
        self.page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        
        if self.is_configured():
            logger.info("Facebook client initialized with Page credentials")
        else:
            logger.warning("Facebook client not configured - missing credentials")
    
    def is_configured(self) -> bool:
        """Check if all required credentials are present."""
        return all([
            self.page_id,
            self.page_access_token
        ])
    
    def post_to_page(
        self,
        message: str,
        link: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Post to the Facebook Page.
        
        We intentionally use the Page feed endpoint (`/{page-id}/feed`) for all
        posts so that they appear in the main \"Posts\"/timeline view, just like
        manual posts made on the Page UI.
        
        Notes:
        - `link` is passed to the feed endpoint, which lets Facebook generate
          a link preview (including an image) using the article's Open Graph
          metadata.
        - `image_url` is currently ignored here. If needed in the future we
          can re-introduce photo posts via `/{page-id}/photos`, but those tend
          to show up primarily under the Photos tab rather than the main feed.
        
        Args:
            message: The post text
            link: Optional URL to include (will generate link preview)
            image_url: Optional image URL (currently unused; kept for API compatibility)
        
        Returns:
            dict with keys:
                - ok: bool indicating success
                - post_id: str post ID if successful
                - error: str error message if failed
        """
        if not self.is_configured():
            return {"ok": False, "error": "Facebook client not configured"}
        
        try:
            # Always post to the Page feed so posts appear in the main feed.
            # Facebook will generate a link preview (with image) from `link`.
            return self._post_feed(message, link)
        except Exception as e:
            logger.error(f"Facebook post error: {e}")
            return {"ok": False, "error": str(e)}
    
    def _post_feed(self, message: str, link: Optional[str] = None) -> Dict:
        """
        Post to the Page's feed (text + optional link preview).
        
        Uses: POST /{page-id}/feed
        """
        url = f"{self.GRAPH_API_BASE}/{self.page_id}/feed"
        
        params = {
            "access_token": self.page_access_token,
            "message": message
        }
        
        if link:
            params["link"] = link
        
        try:
            response = requests.post(url, data=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                post_id = data.get("id")
                return {"ok": True, "post_id": post_id}
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", str(error_data))
                return {"ok": False, "error": f"Graph API error ({response.status_code}): {error_msg}"}
                
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": f"Request failed: {e}"}
    
    def _post_photo(
        self,
        caption: str,
        image_url: str,
        link: Optional[str] = None
    ) -> Dict:
        """
        Post a photo to the Page.
        
        Uses: POST /{page-id}/photos
        
        Note: The image_url must be publicly accessible for Facebook to fetch it.
        """
        url = f"{self.GRAPH_API_BASE}/{self.page_id}/photos"
        
        # Include link in caption if provided
        full_caption = f"{caption}\n\n{link}" if link else caption
        
        params = {
            "access_token": self.page_access_token,
            "caption": full_caption,
            "url": image_url  # Facebook will fetch this URL
        }
        
        try:
            response = requests.post(url, data=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                post_id = data.get("post_id") or data.get("id")
                return {"ok": True, "post_id": post_id}
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", str(error_data))
                
                # If photo upload fails, fall back to feed post
                if "photo" in error_msg.lower() or "image" in error_msg.lower():
                    logger.warning(f"Photo upload failed, falling back to feed post: {error_msg}")
                    return self._post_feed(caption, link)
                
                return {"ok": False, "error": f"Graph API error ({response.status_code}): {error_msg}"}
                
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": f"Request failed: {e}"}

