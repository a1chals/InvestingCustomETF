import os
<<<<<<< HEAD:InvestingCustomETF/custom-etf-builder/backend/clients/perplexity_client.py
from typing import Dict, Any, Optional, Union
import httpx
=======
from typing import Dict, Any
import httpx
import json
>>>>>>> 6c3b6cf7abe6754e34c63367c6e1e26ab64817d6:custom-etf-builder/backend/clients/perplexity_client.py

PERPLEXITY_API_URL = os.getenv('PERPLEXITY_API_URL', 'https://api.perplexity.ai')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')


class PerplexityClient:
<<<<<<< HEAD:InvestingCustomETF/custom-etf-builder/backend/clients/perplexity_client.py
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout_seconds: int = 30) -> None:
=======
    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout_seconds: int = 60) -> None:
>>>>>>> 6c3b6cf7abe6754e34c63367c6e1e26ab64817d6:custom-etf-builder/backend/clients/perplexity_client.py
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
<<<<<<< HEAD:InvestingCustomETF/custom-etf-builder/backend/clients/perplexity_client.py
                    'content': 'You are a research assistant that extracts relevant public companies, tickers, sectors, prices, and market context related to the user\'s text. Return structured JSON with companies array and market_context object.'
                },
                {
                    'role': 'user',
                    'content': f'Based on this text: "{user_text}"\n\nReturn JSON with:\n{{\n  "companies": [{{\n    "symbol": "TICKER",\n    "name": "Company Name",\n    "sector": "Industry Sector",\n    "description": "Brief description"\n  }}],\n  "market_context": {{\n    "themes": ["theme1", "theme2"],\n    "sentiment": "positive/negative/neutral"\n  }}\n}}'
                }
            ],
            'max_tokens': 1200,
            'temperature': 0.2,
=======
                    'content': 'You are an expert financial research analyst specializing in thematic investment discovery. Your role is to identify comprehensive public company investment opportunities that align with user sentiment while providing detailed market intelligence for portfolio construction.\n\nCORE OBJECTIVES:\n1. Extract 1-3 primary investment themes from user text with confidence scoring\n2. Provide 20-30 diverse public companies spanning multiple risk profiles\n3. Ensure broad sector and geographic diversification within themes\n4. Deliver current market context and sentiment analysis\n\nCOMPANY SELECTION CRITERIA:\n- Prioritize liquid stocks (market cap >$1B, average daily volume >1M shares)\n- Include companies at different growth stages and geographies when relevant\n- Focus on pure-play and best-in-class companies for each theme\n- Ensure sub-sector diversification within broader themes\n\nRISK CATEGORIZATION (Critical for downstream portfolio construction):\n- LOW RISK: Large-cap (>$50B), dividend-paying, established market leaders, defensive sectors\n- MEDIUM RISK: Mid-cap ($5B-$50B), profitable growth companies, cyclical sectors\n- HIGH RISK: Small-cap (<$5B), unprofitable/speculative, emerging technologies, volatile sectors\n\nOUTPUT: Return comprehensive structured JSON for systematic portfolio analysis.'
                },
                {
                    'role': 'user',
                    'content': f'Analyze this investment sentiment: "{user_text}"\n\nReturn detailed JSON in this exact format:\n\n{{\n  "analysis_summary": {{\n    "primary_sentiment": "bullish|bearish|neutral|mixed",\n    "confidence_level": 0.0-1.0,\n    "investment_horizon": "short-term|medium-term|long-term"\n  }},\n  "themes_identified": [\n    {{\n      "theme": "descriptive_theme_name",\n      "confidence": 0.0-1.0,\n      "market_size": "estimated TAM or market description",\n      "growth_drivers": ["driver1", "driver2"],\n      "key_risks": ["risk1", "risk2"]\n    }}\n  ],\n  "companies": [\n    {{\n      "symbol": "TICKER",\n      "name": "Full Company Name",\n      "sector": "GICS Sector",\n      "industry": "Specific Industry",\n      "market_cap_billions": 123.45,\n      "risk_category": "low|medium|high",\n      "theme_relevance": "primary_theme_name",\n      "investment_thesis": "2-3 sentence compelling rationale",\n      "current_price_range": "$XXX-$XXX",\n      "key_metrics": {{\n        "revenue_growth": "XX% (if available)",\n        "profit_margin": "XX% (if available)",\n        "geographic_exposure": "primary markets served"\n      }},\n      "competitive_position": "market leader|challenger|niche player"\n    }}\n  ],\n  "market_context": {{\n    "current_environment": "detailed market backdrop for identified themes",\n    "sector_rotation": "any notable sector trends affecting these companies",\n    "macro_factors": ["factor1", "factor2"],\n    "timing_considerations": "market timing insights for these themes",\n    "risk_assessment": "overall risk environment for suggested companies"\n  }}\n}}\n\nTARGET DISTRIBUTION:\n- 8-12 LOW RISK companies (large-cap leaders across themes)\n- 10-15 MEDIUM RISK companies (growth stories and established players)\n- 5-8 HIGH RISK companies (speculative plays and emerging leaders)\n\nEnsure geographic diversity (US, international developed, emerging markets when relevant) and sub-sector diversity within each theme. Prioritize companies with strong fundamentals, clear competitive advantages, and direct exposure to identified themes.'
                }
            ],
            'max_tokens': 7500,
            'temperature': 0.1,
>>>>>>> 6c3b6cf7abe6754e34c63367c6e1e26ab64817d6:custom-etf-builder/backend/clients/perplexity_client.py
        }
        url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                raise RuntimeError(f'Perplexity API error: {resp.status_code} {resp.text}')
            data = resp.json()
            # Expecting OpenAI-compatible schema with choices[0].message.content
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
<<<<<<< HEAD:InvestingCustomETF/custom-etf-builder/backend/clients/perplexity_client.py
            # For MVP, assume content is JSON or JSON-like; attempt to parse
            try:
                import json
                parsed = json.loads(content)
            except Exception:
                parsed = {'raw_content': content}
            return parsed
=======
            # Enhanced error handling for JSON parsing
            if not content:
                raise RuntimeError(f'Empty response from Perplexity API: {data}')
            try:
                parsed = json.loads(content)
                return parsed
            except json.JSONDecodeError as e:
                # Log the actual content for debugging
                raise RuntimeError(f'Invalid JSON response from Perplexity: {e}. Content: {content[:500]}...')
            except Exception as e:
                raise RuntimeError(f'Unexpected error parsing Perplexity response: {e}')
>>>>>>> 6c3b6cf7abe6754e34c63367c6e1e26ab64817d6:custom-etf-builder/backend/clients/perplexity_client.py
