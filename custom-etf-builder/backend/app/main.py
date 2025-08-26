import os
import sys
from pathlib import Path
from dotenv import load_dotenv

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
    # 1) Fetch market context from Perplexity
    try:
        perplexity = PerplexityClient()
        market_data = await perplexity.fetch_market_context(req.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'Perplexity error: {e}')

    # 2) Ask GPT-4o for allocations
    try:
        gpt = GPT4oProcessor()
        raw = await gpt.generate_portfolio(req.text, req.risk, req.amount, market_data)
        portfolio_allocations = raw.get('portfolio_allocations', [])
        themes_detected = raw.get('themes_detected', [])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'OpenAI error: {e}')

    if not portfolio_allocations:
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
