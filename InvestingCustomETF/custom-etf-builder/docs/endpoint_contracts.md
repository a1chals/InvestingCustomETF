# Endpoint Contract

## POST /generate_portfolio

### Request JSON
```json
{
  "text": "I think EV fleets will explode. I see a lot of chargers popping up.",
  "risk": "low|medium|high",
  "amount": 5000
}
```

### Response JSON
```json
{
  "as_of": "YYYY-MM-DD",
  "holdings": [
    { "symbol": "TSLA", "weight": 0.15, "kind": "stock", "rationale": "Leading EV manufacturer with charging network expansion" },
    { "symbol": "CHPT", "weight": 0.08, "kind": "stock", "rationale": "Pure-play charging infrastructure growth" },
    { "symbol": "VTI",  "weight": 0.45, "kind": "etf", "rationale": "Broad market diversification for risk management" }
  ],
  "notes": {
    "themes_detected": [
      { "theme": "electric_vehicles", "confidence": 0.9, "evidence": ["EV fleets will explode", "chargers popping up"] },
      { "theme": "charging_infrastructure", "confidence": 0.8, "evidence": ["lot of chargers popping up"] }
    ],
    "risk_profile": "medium",
    "binding_constraints": ["single_name_cap", "sector_concentration_limit"],
    "rationale_summary": [
      "High conviction in EV/charging theme based on user observations",
      "Balanced with broad market exposure for risk management", 
      "Real-time market data confirms sector momentum"
    ],
    "data_sources": ["Perplexity API", "GPT-4o"],
    "disclaimer": "This tool is for educational purposes only and does not constitute investment advice."
  }
}
```

### Behavior Notes
- If Perplexity API is unavailable, return error with retry suggestion rather than fallback data.
- GPT-4o processes both user sentiment and real-time Perplexity market data for allocations.
- Risk level affects allocation: Low = stable large-cap focus, Medium = balanced, High = aggressive growth-oriented.
- All portfolio weights are AI-generated but validated against basic risk constraints. 