from typing import Dict, Any, List
from datetime import date
import sys
from pathlib import Path

# Add parent directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from models.schemas import PortfolioAllocation, Notes


def format_response(as_of: str, allocations: List[PortfolioAllocation], risk: str, themes: List[Dict[str, Any]], binding_constraints: List[str]) -> Dict[str, Any]:
    notes = Notes(
        themes_detected=themes,
        risk_profile=risk,  # type: ignore
        binding_constraints=binding_constraints,
        rationale_summary=[
            'Allocations reflect user sentiment while respecting risk constraints',
            'Broad market ETFs included for diversification',
        ],
        data_sources=['Perplexity API', 'GPT-4o'],
        disclaimer='This tool is for educational purposes only and does not constitute investment advice.'
    )

    return {
        'as_of': as_of or date.today().isoformat(),
        'holdings': [h.model_dump() for h in allocations],
        'notes': notes.model_dump(),
    }
