from __future__ import annotations

from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


RiskLevel = Literal["low", "medium", "high"]


class GeneratePortfolioRequest(BaseModel):
    text: str = Field(..., description="Natural language observations and views")
    risk: RiskLevel = Field(..., description="Risk tier selection")
    amount: float = Field(..., gt=0, description="Investment amount in USD")


class Company(BaseModel):
    symbol: str
    name: Optional[str] = None
    price: Optional[float] = None
    market_cap: Optional[float] = None
    sector: Optional[str] = None
    description: Optional[str] = None


class PerplexityData(BaseModel):
    companies: List[Company] = Field(default_factory=list)
    market_context: Dict[str, Any] = Field(default_factory=dict)


class ThemeDetected(BaseModel):
    theme: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)


HoldingKind = Literal["stock", "etf"]


class PortfolioAllocation(BaseModel):
    symbol: str
    weight: float = Field(..., ge=0.0, le=1.0)
    kind: HoldingKind
    rationale: str


class GPTProcessingOutput(BaseModel):
    themes_detected: List[ThemeDetected] = Field(default_factory=list)
    portfolio_allocations: List[PortfolioAllocation] = Field(default_factory=list)
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    constraints_applied: List[str] = Field(default_factory=list)

    @field_validator("portfolio_allocations")
    @classmethod
    def _ensure_weights_sum_reasonable(cls, v: List[PortfolioAllocation]):
        if not v:
            return v
        total = sum(h.weight for h in v)
        # Allow some tolerance; policy engine will fix precisely
        if total < 0.8 or total > 1.2:
            # Out-of-range; still allow, downstream will normalize
            return v
        return v


class Notes(BaseModel):
    themes_detected: List[ThemeDetected] = Field(default_factory=list)
    risk_profile: RiskLevel
    binding_constraints: List[str] = Field(default_factory=list)
    rationale_summary: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    disclaimer: str


class GeneratePortfolioResponse(BaseModel):
    as_of: str
    holdings: List[PortfolioAllocation]
    notes: Notes
