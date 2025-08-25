# Input Contract (GPT-4o Processing)

## Simplified Input Processing

With Perplexity API + GPT-4o, the input contract is streamlined:

### User Input
- **text**: Natural language observations (e.g., "I think EV fleets will explode. I see a lot of chargers popping up.")
- **risk**: Simple risk level (low | medium | high)  
- **amount**: Investment amount in USD

### GPT-4o Processing Output
```json
{
  "themes_detected": [
    {
      "theme": "electric_vehicles",
      "confidence": 0.9,
      "evidence": ["EV fleets will explode", "charging infrastructure expansion"]
    }
  ],
  "risk_assessment": {
    "user_risk_level": "medium",
    "sentiment_indicators": ["optimistic", "growth-oriented"],
    "investment_horizon": "medium_term"
  },
  "market_relevance": {
    "sectors_identified": ["automotive", "energy_infrastructure"],
    "conviction_level": "high"
  }
}
```

### Notes
- GPT-4o directly processes user text without complex intermediate schemas
- Perplexity provides real-time company/market data dynamically
- No need for static theme allowlists - AI discovers relevant stocks in real-time
- Simplified risk mapping: low=conservative, medium=balanced, high=aggressive 