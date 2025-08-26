import os
from typing import Dict, Any, List

from openai import AsyncOpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

SYSTEM_PROMPT = (
    'You are a professional portfolio advisor that generates personalized stock allocations based on user sentiment and real-time market data.\n'
    'INPUTS:\n- User text: Natural language observations about market trends\n- Risk level: low/medium/high\n- Amount: Investment amount in USD\n- Market data: Real-time company information from Perplexity API\n\n'
    'RISK CONSTRAINTS:\n- Low risk: Max 20% theme exposure, 5% single stock, 70% diversified ETFs\n- Medium risk: Max 40% theme exposure, 8% single stock, 50% diversified ETFs\n- High risk: Max 60% theme exposure, 12% single stock, 30% diversified ETFs\n\n'
    'REQUIREMENTS:\n1. Identify 1-3 investment themes from user text with confidence scores\n2. Generate portfolio allocations respecting risk constraints\n3. Provide clear rationale for each holding\n4. Ensure total weights sum to 100%\n5. Include broad market ETFs for diversification\n\n'
    'OUTPUT FORMAT: Return ONLY valid JSON in this exact format:\n'
    '{\n'
    '  "themes_detected": [{"theme": "electric_vehicles", "confidence": 0.9, "evidence": ["EV companies will dominate"]}],\n'
    '  "portfolio_allocations": [\n'
    '    {"symbol": "TSLA", "weight": 0.15, "kind": "stock", "rationale": "Leading EV manufacturer"},\n'
    '    {"symbol": "VTI", "weight": 0.50, "kind": "etf", "rationale": "Broad market diversification"}\n'
    '  ]\n'
    '}'
)


class GPT4oProcessor:
    def __init__(self, api_key: str | None = None, model: str = 'gpt-4o-mini') -> None:
        self.client = AsyncOpenAI(api_key=api_key or OPENAI_API_KEY)
        self.model = model

    async def generate_portfolio(self, user_text: str, risk: str, amount: float, market_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            { 'role': 'system', 'content': SYSTEM_PROMPT },
            { 'role': 'user', 'content': f'User text: {user_text}\nRisk: {risk}\nAmount: {amount}\nMarket data (JSON): {market_data}\nReturn ONLY JSON.' }
        ]
        resp = await self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.2, max_tokens=1200)
        content = resp.choices[0].message.content
        import json
        try:
            return json.loads(content)
        except Exception:
            return { 'raw_content': content }
