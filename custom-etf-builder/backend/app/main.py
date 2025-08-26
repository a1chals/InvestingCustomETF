import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import uuid

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(dotenv_path=env_path)

# Add parent directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import GeneratePortfolioRequest, GeneratePortfolioResponse, PortfolioAllocation
from clients.perplexity_client import PerplexityClient
from services.gpt4o_processor import GPT4oProcessor
from services.policy_engine import enforce_policy
from services.portfolio_formatter import format_response

DEBUG_AI = os.getenv('DEBUG_AI', '') == '1'
USE_PERPLEXITY_STUB = os.getenv('USE_PERPLEXITY_STUB', '') == '1'

app = FastAPI(title='Sentiment-Driven Stock Portfolio Generator (MVP)')

# CORS (allow all for MVP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/generate_portfolio')
async def generate_portfolio(req: GeneratePortfolioRequest):
    cid = str(uuid.uuid4())[:8]
    if DEBUG_AI:
        try:
            print(f"[CID {cid}] start text_len={len(req.text)}, risk={req.risk}, amount={req.amount}")
        except Exception:
            pass
    # 1) Fetch market context from Perplexity
    try:
        if DEBUG_AI and USE_PERPLEXITY_STUB:
            market_data = {
                "companies": [
                    {"symbol": "AAPL", "name": "Apple", "sector": "Information Technology", "description": "Large-cap anchor"},
                    {"symbol": "MSFT", "name": "Microsoft", "sector": "Information Technology", "description": "Large-cap anchor"},
                    {"symbol": "NVDA", "name": "NVIDIA", "sector": "Information Technology", "description": "Growth"}
                ],
                "market_context": {"themes": ["mega-cap tech"], "sentiment": "positive"}
            }
            if DEBUG_AI:
                print(f"[CID {cid}] using Perplexity STUB companies={len(market_data['companies'])}")
        else:
            perplexity = PerplexityClient()
            market_data = await perplexity.fetch_market_context(req.text)
        if DEBUG_AI:
            try:
                md_companies = len(market_data.get('companies', [])) if isinstance(market_data, dict) else 0
                print(f"[CID {cid}] perplexity ok companies={md_companies}")
            except Exception:
                pass
    except Exception as e:
        if DEBUG_AI:
            print(f"[CID {cid}] perplexity error: {e}")
        raise HTTPException(status_code=502, detail=f'Perplexity error: {e}')

    # 2) Ask GPT-4o for allocations
    try:
        gpt = GPT4oProcessor()
        raw = await gpt.generate_portfolio(req.text, req.risk, req.amount, market_data)
        if DEBUG_AI:
            try:
                print(f"[CID {cid}] gpt4o keys={list(raw.keys())[:8]}")
            except Exception:
                pass
        portfolio_allocations = raw.get('portfolio_allocations', [])
        themes_detected = raw.get('themes_detected', [])
    except Exception as e:
        if DEBUG_AI:
            print(f"[CID {cid}] openai error: {e}")
        raise HTTPException(status_code=502, detail=f'OpenAI error: {e}')

    if not portfolio_allocations:
        if DEBUG_AI:
            try:
                print(f"[CID {cid}] empty allocations. raw preview={str(raw)[:400]}")
            except Exception:
                pass
        raise HTTPException(status_code=500, detail='AI did not return any allocations')

    # 3) Convert to models and enforce policy
    try:
        allocations = [
            PortfolioAllocation(
                symbol=h.get('symbol'),
                weight=float(h.get('weight', 0.0)),
                kind=h.get('kind', 'stock'),
                rationale=h.get('rationale', ''),
            ) for h in portfolio_allocations
        ]
    except Exception as e:
        if DEBUG_AI:
            print(f"[CID {cid}] allocation parse error: {e}")
        raise HTTPException(status_code=500, detail=f'Invalid allocation format: {e}')

    policy_out = enforce_policy(req.risk, allocations)

    # 4) Format response
    resp = format_response(
        as_of=policy_out['as_of'],
        allocations=policy_out['validated_portfolio'],
        risk=req.risk,
        themes=themes_detected,
        binding_constraints=policy_out['binding_constraints'],
    )

    return resp
