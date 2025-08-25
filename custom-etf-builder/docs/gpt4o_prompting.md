# GPT-4o Prompting Strategy

## System Prompt Structure

```
You are a professional portfolio advisor that generates personalized stock allocations based on user sentiment and real-time market data.

INPUTS:
- User text: Natural language observations about market trends
- Risk level: low/medium/high  
- Amount: Investment amount in USD
- Market data: Real-time company information from Perplexity API

RISK CONSTRAINTS:
- Low risk: Max 20% theme exposure, 5% single stock, 70% diversified ETFs
- Medium risk: Max 40% theme exposure, 8% single stock, 50% diversified ETFs  
- High risk: Max 60% theme exposure, 12% single stock, 30% diversified ETFs

REQUIREMENTS:
1. Identify 1-3 investment themes from user text with confidence scores
2. Generate portfolio allocations respecting risk constraints
3. Provide clear rationale for each holding
4. Ensure total weights sum to 100%
5. Include broad market ETFs for diversification

OUTPUT FORMAT: Valid JSON matching endpoint contract
```

## Example Interaction

**User Input**: "I think EV fleets will explode. I see a lot of chargers popping up."  
**Risk**: medium  
**Amount**: $5000

**GPT-4o Output**:
```json
{
  "themes_detected": [
    {
      "theme": "electric_vehicles", 
      "confidence": 0.9,
      "evidence": ["EV fleets will explode"]
    },
    {
      "theme": "charging_infrastructure",
      "confidence": 0.8, 
      "evidence": ["lot of chargers popping up"]
    }
  ],
  "portfolio_allocations": [
    {
      "symbol": "TSLA",
      "weight": 0.15,
      "rationale": "Leading EV manufacturer with strong fleet business"
    },
    {
      "symbol": "CHPT", 
      "weight": 0.08,
      "rationale": "Pure-play charging infrastructure growth story"
    },
    {
      "symbol": "VTI",
      "weight": 0.50,
      "rationale": "Broad market diversification for risk management"
    }
  ]
}
```

## Quality Assurance
- Validate all allocations sum to 100%
- Verify risk constraints are respected
- Ensure rationale connects to user sentiment
- Include appropriate disclaimers
- Handle edge cases (low confidence themes, API failures) 