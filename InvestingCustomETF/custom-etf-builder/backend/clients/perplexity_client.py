import os
from typing import Dict, Any, Optional, Union
import httpx

PERPLEXITY_API_URL = os.getenv('PERPLEXITY_API_URL', 'https://api.perplexity.ai')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')


class PerplexityClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout_seconds: int = 30) -> None:
        self.api_key = api_key or PERPLEXITY_API_KEY
        self.base_url = base_url or PERPLEXITY_API_URL
        self.timeout_seconds = timeout_seconds

    async def fetch_market_context(self, user_text: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('PERPLEXITY_API_KEY not configured')
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': 'sonar',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a research assistant that extracts relevant public companies, tickers, sectors, prices, and market context related to the user\'s text. Return structured JSON with companies array and market_context object.'
                },
                {
                    'role': 'user',
                    'content': f'Based on this text: "{user_text}"\n\nReturn JSON with:\n{{\n  "companies": [{{\n    "symbol": "TICKER",\n    "name": "Company Name",\n    "sector": "Industry Sector",\n    "description": "Brief description"\n  }}],\n  "market_context": {{\n    "themes": ["theme1", "theme2"],\n    "sentiment": "positive/negative/neutral"\n  }}\n}}'
                }
            ],
            'max_tokens': 1200,
            'temperature': 0.2,
        }
        url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                raise RuntimeError(f'Perplexity API error: {resp.status_code} {resp.text}')
            data = resp.json()
            # Expecting OpenAI-compatible schema with choices[0].message.content
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            # For MVP, assume content is JSON or JSON-like; attempt to parse
            try:
                import json
                parsed = json.loads(content)
            except Exception:
                parsed = {'raw_content': content}
            return parsed
