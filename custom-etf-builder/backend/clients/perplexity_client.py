import os
from typing import Dict, Any, Optional
import httpx
import json

PERPLEXITY_API_URL = os.getenv('PERPLEXITY_API_URL', 'https://api.perplexity.ai')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')
DEBUG_AI = os.getenv('DEBUG_AI', '') == '1'


class PerplexityClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout_seconds: int = 60) -> None:
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
                    'content': 'You are an expert financial research analyst specializing in thematic investment discovery. Your role is to identify comprehensive public company investment opportunities that align with user sentiment while providing detailed market intelligence for portfolio construction.\n\nCORE OBJECTIVES:\n1. Extract 1-3 primary investment themes from user text with confidence scoring\n2. Provide 12-15 diverse public companies spanning multiple risk profiles\n3. Ensure broad sector and geographic diversification within themes\n4. Deliver current market context and sentiment analysis\n\nCOMPANY SELECTION CRITERIA:\n- Prioritize liquid stocks (market cap >$1B, average daily volume >1M shares)\n- Include companies at different growth stages and geographies when relevant\n- Focus on pure-play and best-in-class companies for each theme\n- Ensure sub-sector diversification within broader themes\n\nRISK CATEGORIZATION (Critical for downstream portfolio construction):\n- LOW RISK: Large-cap (>$50B), dividend-paying, established market leaders, defensive sectors\n- MEDIUM RISK: Mid-cap ($5B-$50B), profitable growth companies, cyclical sectors\n- HIGH RISK: Small-cap (<$5B), unprofitable/speculative, emerging technologies, volatile sectors\n\nOUTPUT: Return ONLY raw JSON without markdown formatting or code blocks.'
                },
                {
                    'role': 'user',
                    'content': f'Analyze this investment sentiment: "{user_text}"\n\nReturn ONLY raw JSON (no markdown, no code blocks) in this exact format:\n\n{{\n  "analysis_summary": {{\n    "primary_sentiment": "bullish|bearish|neutral|mixed",\n    "confidence_level": 0.0-1.0,\n    "investment_horizon": "short-term|medium-term|long-term"\n  }},\n  "themes_identified": [\n    {{\n      "theme": "descriptive_theme_name",\n      "confidence": 0.0-1.0,\n      "market_size": "estimated TAM or market description",\n      "growth_drivers": ["driver1", "driver2"],\n      "key_risks": ["risk1", "risk2"]\n    }}\n  ],\n  "companies": [\n    {{\n      "symbol": "TICKER",\n      "name": "Full Company Name",\n      "sector": "GICS Sector",\n      "industry": "Specific Industry",\n      "market_cap_billions": 123.45,\n      "risk_category": "low|medium|high",\n      "theme_relevance": "primary_theme_name",\n      "investment_thesis": "2-3 sentence compelling rationale",\n      "current_price_range": "$XXX-$XXX",\n      "key_metrics": {{\n        "revenue_growth": "XX% (if available)",\n        "profit_margin": "XX% (if available)",\n        "geographic_exposure": "primary markets served"\n      }},\n      "competitive_position": "market leader|challenger|niche player"\n    }}\n  ],\n  "market_context": {{\n    "current_environment": "detailed market backdrop for identified themes",\n    "sector_rotation": "any notable sector trends affecting these companies",\n    "macro_factors": ["factor1", "factor2"],\n    "timing_considerations": "market timing insights for these themes",\n    "risk_assessment": "overall risk environment for suggested companies"\n  }}\n}}\n\nTARGET DISTRIBUTION (12-15 total companies):\n- 4-6 LOW RISK companies (large-cap leaders across themes)\n- 5-7 MEDIUM RISK companies (growth stories and established players)\n- 3-4 HIGH RISK companies (speculative plays and emerging leaders)\n\nIMPORTANT: Return ONLY the JSON object. Do not wrap in markdown code blocks or use ```json formatting. Start directly with the opening brace.'
                }
            ],
            'max_tokens': 7500,
            'temperature': 0.1,
        }
        url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                raise RuntimeError(f'Perplexity API error: {resp.status_code} {resp.text}')
            data = resp.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

            # Strip markdown code fences if present
            if content.startswith('```'):
                fence = '```json'
                if content.startswith(fence):
                    content = content[len(fence):]
                elif content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()

            if DEBUG_AI:
                try:
                    print(f"[PERPLEXITY] content_len={len(content)}")
                    print(f"[PERPLEXITY] head: {content[:300]}")
                    print(f"[PERPLEXITY] tail: {content[-300:]}")
                except Exception:
                    pass

            if not content:
                raise RuntimeError(f'Empty response from Perplexity API: {data}')
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError as e:
                raise RuntimeError(f'Invalid JSON response from Perplexity: {e}. Content: {content[:500]}...')

            # Debug-only clamp to reduce downstream size
            if DEBUG_AI and isinstance(parsed, dict) and isinstance(parsed.get('companies'), list):
                parsed['companies'] = parsed['companies'][:12]
                print(f"[PERPLEXITY] debug clamp companies={len(parsed['companies'])}")

            return parsed
