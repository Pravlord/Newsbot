"""
LLM rewriter using OpenRouter API for rewriting articles.
"""
import os
from typing import Dict, Optional
from openai import OpenAI


class LLMRewriter:
    """Rewrite articles using OpenRouter (OpenAI-compatible API)."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.provider = config.get('provider', 'openrouter')
        self.model = config.get('model', 'openai/gpt-4')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 500)
        self.prompt_template = config.get('rewrite_prompt', '')
        
        # Initialize OpenRouter client (uses OpenAI-compatible API)
        api_key = os.getenv(config.get('api_key_env', 'OPENROUTER_API_KEY'))
        if api_key:
            # OpenRouter uses OpenAI-compatible API with base_url override
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
            self.client = None
            print("⚠ Warning: OPENROUTER_API_KEY not found in environment")
    
    def rewrite_article(self, article: Dict) -> Optional[str]:
        """Rewrite article content using OpenRouter LLM."""
        if not self.client:
            return None
        
        # Build prompt
        content = article.get('original_content') or article.get('summary', '')
        if not content:
            content = article.get('content', '')
        
        # Limit content length to avoid token limits
        content_preview = content[:2000] if len(content) > 2000 else content
        
        prompt = f"""{self.prompt_template}

Original Article:
Title: {article.get('title', '')}
Content: {content_preview}

Rewrite the above article for social media:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional news writer. Output ONLY a single short post. No emojis. No multiple options. No headers. Just the post text and hashtags."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            rewritten_text = response.choices[0].message.content.strip()
            return rewritten_text
            
        except Exception as e:
            print(f"  ⚠ LLM error: {e}")
            return None


