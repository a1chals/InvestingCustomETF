from typing import List, Dict, Any
from datetime import date
import sys
from pathlib import Path

# Add parent directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from models.schemas import PortfolioAllocation, RiskLevel


RISK_POLICY = {
    'low':    { 'max_theme_exposure': 0.20, 'max_single_stock': 0.05, 'min_diversified_etf': 0.70 },
    'medium': { 'max_theme_exposure': 0.40, 'max_single_stock': 0.08, 'min_diversified_etf': 0.50 },
    'high':   { 'max_theme_exposure': 0.60, 'max_single_stock': 0.12, 'min_diversified_etf': 0.30 },
}


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def normalize_weights(holdings: List[PortfolioAllocation]) -> List[PortfolioAllocation]:
    total = sum(h.weight for h in holdings) or 1.0
    return [PortfolioAllocation(symbol=h.symbol, weight=h.weight / total, kind=h.kind, rationale=h.rationale) for h in holdings]


def enforce_policy(risk: RiskLevel, raw_allocs: List[PortfolioAllocation]) -> Dict[str, Any]:
    policy = RISK_POLICY[risk]
    binding_constraints: List[str] = []

    # Single stock cap
    adjusted = []
    for h in raw_allocs:
        if h.weight > policy['max_single_stock']:
            binding_constraints.append('single_name_cap')
            adjusted.append(PortfolioAllocation(symbol=h.symbol, weight=policy['max_single_stock'], kind=h.kind, rationale=h.rationale))
        else:
            adjusted.append(h)

    # Diversification floor (ensure ETFs min allocation)
    etf_total = sum(h.weight for h in adjusted if h.kind == 'etf')
    if etf_total < policy['min_diversified_etf']:
        binding_constraints.append('diversification_floor')
        deficit = policy['min_diversified_etf'] - etf_total
        # Increase ETF weights proportionally, reduce stocks proportionally
        stocks = [h for h in adjusted if h.kind == 'stock']
        etfs = [h for h in adjusted if h.kind == 'etf']
        stock_total = sum(h.weight for h in stocks)
        if stock_total > 0 and etfs:
            reduce_ratio = deficit / stock_total
            new_adjusted: List[PortfolioAllocation] = []
            for h in adjusted:
                if h.kind == 'stock':
                    new_weight = clamp(h.weight * (1 - reduce_ratio), 0.0, h.weight)
                    new_adjusted.append(PortfolioAllocation(symbol=h.symbol, weight=new_weight, kind=h.kind, rationale=h.rationale))
                else:
                    # increase ETF proportionally
                    etf_increase = deficit * (h.weight / (etf_total or 1.0))
                    new_adjusted.append(PortfolioAllocation(symbol=h.symbol, weight=h.weight + etf_increase, kind=h.kind, rationale=h.rationale))
            adjusted = new_adjusted

    # Normalize to sum 1.0
    adjusted = normalize_weights(adjusted)

    return {
        'validated_portfolio': adjusted,
        'binding_constraints': list(sorted(set(binding_constraints))),
        'as_of': date.today().isoformat(),
    }
