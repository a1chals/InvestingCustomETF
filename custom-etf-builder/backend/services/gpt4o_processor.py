import os
from typing import Dict, Any, List

from openai import AsyncOpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
DEBUG_AI = os.getenv('DEBUG_AI', '') == '1'

SYSTEM_PROMPT = (
    "You are the portfolio weights composer. You receive:\n"
    "- The user’s free-text observation\n"
    "- A list of candidate stocks from Perplexity\n"
    "- A simple risk level (low/medium/high)\n\n"

    "Your job is to allocate weights across those stocks only. "
    "Do not fetch new tickers, do not add ETFs, funds, or cash. "
    "You must follow the rules below and return ONLY valid JSON in the required schema.\n\n"

    "-----------------------------------------\n"
    "INPUT FORMAT (you will be given):\n"
    "{\n"
    "  \"as_of\": \"YYYY-MM-DD\",\n"
    "  \"user\": {\n"
    "    \"text\": \"<original user text>\",\n"
    "    \"amount_usd\": 5000,\n"
    "    \"risk_level\": \"low|medium|high\"\n"
    "  },\n"
    "  \"perplexity_metadata\": {\n"
    "    \"companies\": [\n"
    "      { \"symbol\": \"TICKER\", \"name\": \"Company Name\", \"sector\": \"Industry Sector\", \"description\": \"Brief description\" }\n"
    "    ],\n"
    "    \"market_context\": { \"themes\": [\"theme1\",\"theme2\"], \"sentiment\": \"positive|negative|neutral\" }\n"
    "  }\n"
    "}\n\n"

    "Use ONLY the companies provided. If any entry looks like an ETF, fund, or trust "
    "(its name/description includes 'ETF', 'Fund', or 'Trust'), exclude it.\n\n"

    "-----------------------------------------\n"
    "RISK DEFINITIONS (stocks-only, anchors vs growth):\n"
    "- Low risk (Conservative): Anchors 80–90%, Growth 10–20%\n"
    "- Medium risk (Balanced): Anchors 50–60%, Growth 40–50%\n"
    "- High risk (Aggressive): Anchors 20–40%, Growth 60–80%\n\n"

    "Caps & Floors per stock:\n"
    "- Low risk: anchor cap 15%, growth cap 5%, floor 1.5%\n"
    "- Medium risk: anchor cap 10%, growth cap 7%, floor 1.0%\n"
    "- High risk: anchor cap 8%,  growth cap 9%, floor 0.8%\n\n"

    "Breadth: Prefer 8–20 total names. If fewer available, use all. If more than 20, keep best fits.\n\n"

    "-----------------------------------------\n"
    "ALLOCATION RULES:\n"
    "1. Classify each candidate as anchor (large, established, diversified) or growth (emerging, volatile).\n"
    "2. Set anchor/growth targets within the ranges above.\n"
    "3. Distribute weights within each bucket (anchors favor largest/stable; growth favor innovative/emerging).\n"
    "4. Enforce per-name caps and floors.\n"
    "5. Repair: If caps bind or not enough names, rebalance within the bucket; if still infeasible, reallocate to the other bucket. Note in 'binding_constraints'.\n"
    "6. Normalize weights so sum = 1.0 (±0.001).\n\n"

    "-----------------------------------------\n"
    "OUTPUT FORMAT (must return ONLY this JSON):\n"
    "{\n"
    "  \"as_of\": \"YYYY-MM-DD\",\n"
    "  \"risk_level\": \"low|medium|high\",\n"
    "  \"themes_detected\": [{\"theme\": \"theme_name\", \"confidence\": 0.9, \"evidence\": [\"supporting_text\"]}],\n"
    "  \"sentiment\": \"positive|negative|neutral\",\n"
    "  \"anchor_growth_targets\": { \"anchor\": 0.00, \"growth\": 0.00 },\n"
    "  \"portfolio_allocations\": [\n"
    "    { \"symbol\": \"TICKER\", \"weight\": 0.00, \"kind\": \"stock\", \"rationale\": \"short reason\" }\n"
    "  ],\n"
    "  \"bucket_actuals\": { \"anchor\": 0.00, \"growth\": 0.00 },\n"
    "  \"binding_constraints\": [\"cap_trim\",\"bucket_rebalance\",\"insufficient_candidates\"],\n"
    "  \"validation\": { \"sum_to_one\": true, \"all_within_caps\": true, \"all_above_floors\": true, \"breadth\": 0 }\n"
    "}\n\n"

    "-----------------------------------------\n"
    "PROCEDURE:\n"
    "1. Filter & classify.\n"
    "2. Set anchor/growth targets within range; record in anchor_growth_targets.\n"
    "3. Allocate pro-rata in each bucket, respecting caps/floors.\n"
    "4. Repair and rebalance as needed; normalize to 1.0.\n"
    "5. Fill validation booleans and constraints.\n"
    "6. Provide compact rationale for each holding from the company description.\n\n"

    "-----------------------------------------\n"
    "If companies array is empty: return portfolio_allocations = [] and set binding_constraints=[\"insufficient_candidates\"].\n"
    "Do not add/remove/rename fields. Do not return anything except the JSON object above.\n"
)



class GPT4oProcessor:
    def __init__(self, api_key: str | None = None, model: str = 'gpt-4o') -> None:
        self.client = AsyncOpenAI(api_key=api_key or OPENAI_API_KEY)
        self.model = model

    async def generate_portfolio(self, user_text: str, risk: str, amount: float, market_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            { 'role': 'system', 'content': SYSTEM_PROMPT },
            { 'role': 'user', 'content': f'User text: {user_text}\nRisk: {risk}\nAmount: {amount}\nMarket data (JSON): {market_data}\nReturn ONLY JSON.' }
        ]

        # Debug: log sizes of incoming market data
        if DEBUG_AI:
            try:
                import json as _json
                md_str = _json.dumps(market_data)
                print(f"[GPT4o] companies_in={len(market_data.get('companies', [])) if isinstance(market_data, dict) else 0}, market_data_len={len(md_str)}")
            except Exception:
                pass

        resp = await self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.2, max_tokens=2000)
        content = resp.choices[0].message.content

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

        # Debug: log usage and finish_reason
        if DEBUG_AI:
            try:
                usage = getattr(resp, 'usage', None)
                finish = resp.choices[0].finish_reason
                print(f"[GPT4o] usage={usage}, finish_reason={finish}")
            except Exception:
                pass

        import json
        try:
            result = json.loads(content)
        except Exception:
            if DEBUG_AI:
                try:
                    print(f"[GPT4o] JSON parse error. content_len={len(content)}")
                    print(f"[GPT4o] head: {content[:300]}")
                    print(f"[GPT4o] tail: {content[-300:]}")
                except Exception:
                    pass
            return { 'raw_content': content }

        # Debug-only fallback mapping if holdings present instead of portfolio_allocations
        if DEBUG_AI and isinstance(result, Dict):
            if not result.get('portfolio_allocations') and isinstance(result.get('holdings'), list):
                mapped = []
                for h in result['holdings']:
                    mapped.append({
                        'symbol': h.get('symbol'),
                        'weight': h.get('weight', 0.0),
                        'kind': h.get('kind', 'stock'),
                        'rationale': h.get('rationale', '')
                    })
                result['portfolio_allocations'] = mapped
                print(f"[GPT4o] mapped holdings->{len(mapped)} portfolio_allocations")

        return result
