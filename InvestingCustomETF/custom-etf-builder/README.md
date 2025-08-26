# Sentiment-Based Stock Portfolio Generator (MVP)

## Problem
Beginners struggle to convert observations (e.g., "EV fleets are exploding") into a diversified portfolio.

## Solution
Natural language input → Perplexity real-time market data → GPT-4o AI reasoning → personalized portfolio JSON → simple visualization.

## Project Structure

```
custom-etf-builder/
├── docs/
│   ├── input_contract.md      # GPT-4o processing specification
│   ├── policy_caps.md         # Simplified risk policy rules
│   ├── themes.md              # Theme taxonomy (reference only)
│   ├── vendors.md             # Perplexity + GPT-4o integration
│   └── endpoint_contracts.md  # API endpoint specifications
├── themes/
│   └── allowlists.json        # Reference data (replaced by dynamic Perplexity queries)
├── frontend/
│   └── UI_CONTRACT.md         # Frontend interface contract
├── backend/
│   └── MODULES.md             # Backend architecture (Perplexity + GPT-4o)
├── compliance/
│   └── explainability.md      # Compliance and explainability rules
└── README.md                  # This file
```

## MVP Scope
- **Input**: Natural language text + risk level (low/medium/high) + amount
- **Processing**: Perplexity API for real-time market data + GPT-4o for AI reasoning
- **Output**: Personalized portfolio allocations with rationale + risk compliance
- **UI**: Minimal web interface with pie chart visualization
- **Compliance**: Educational disclaimers, no actual trading

## Key Advantages
- **Real-time Data**: Perplexity API eliminates need for local market data pipeline
- **AI-Driven**: GPT-4o handles complex sentiment analysis and allocation logic
- **Fast MVP**: No complex data infrastructure or static allowlists required
- **Scalable**: Can handle any user input theme or market observation

## Success Metrics
- Users receive personalized portfolio recommendations for any natural language input
- Recommendations respect risk levels and are logically coherent with user sentiment  
- Real-time market data ensures recommendations stay current and relevant
- MVP demonstrates AI-driven allocation logic with explainable rationale

## Technical Pipeline
1. **User Input**: Free-text observations + risk selection → Frontend form
2. **Perplexity Query**: Extract relevant companies, prices, market cap, sector data
3. **GPT-4o Processing**: Sentiment analysis + portfolio allocation + rationale generation
4. **Policy Validation**: Apply risk constraints and diversification rules
5. **Response**: JSON portfolio + explanations → Frontend visualization

## Run Locally (Implementation Phase)
- Backend: FastAPI app with Perplexity + OpenAI integrations
- Frontend: React app with portfolio visualization
- Environment: PERPLEXITY_API_KEY, OPENAI_API_KEY

## Acceptance Criteria

**Test Scenario**: "I think EV fleets will explode. I see a lot of chargers popping up." + Medium risk + $5,000

Expected Results:
- Portfolio includes 20-40% allocation to EV/charging themes (medium risk limits)
- Individual stock positions ≤ 8% (single stock cap for medium risk)
- 50%+ allocated to broad diversification ETFs (risk management)
- Response includes: themes_detected, binding_constraints, rationale_summary, real-time data sources
- If APIs unavailable: clear error message with retry guidance (no fallback data) 