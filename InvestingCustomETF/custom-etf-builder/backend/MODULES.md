# Backend Modules (Planned)

## perplexity_client
- Purpose: Fetch real-time market data, company information, prices, market cap, and sector data
- Input: user text + extracted themes/companies
- Output: { companies: [{ symbol, name, price, market_cap, sector, description }], market_context: {...} }
- Env: PERPLEXITY_API_KEY
- Note: Dynamically retrieves relevant companies based on user sentiment, no static allowlists needed.

## gpt4o_processor
- Purpose: Interpret user sentiment, map to investment themes, and generate portfolio allocations using Perplexity data
- Input: { user_text, risk_level, perplexity_data }
- Output: { 
    themes_detected: [{ theme, confidence, evidence }],
    portfolio_allocations: [{ symbol, weight, rationale }],
    risk_assessment: {...},
    constraints_applied: [...]
  }
- Env: OPENAI_API_KEY
- Note: Uses structured prompting to ensure consistent JSON output format.

## policy_engine
- Purpose: Apply risk-based constraints and validate portfolio allocations
- Input: { risk_level, raw_allocations }
- Output: { validated_portfolio, binding_constraints, adjustments_made }
- Note: Ensures allocations respect risk tier limits (conservative/moderate/aggressive).

## portfolio_formatter
- Purpose: Format final portfolio response with rationale and compliance notes
- Inputs: validated portfolio, market data, user context
- Outputs: standardized JSON response matching endpoint contract
- Note: Includes disclaimers, data sources, timestamps, and explainability elements.

## app (FastAPI)
- Expose POST `/generate_portfolio`
- Orchestrates: user input → perplexity_client → gpt4o_processor → policy_engine → portfolio_formatter → response JSON
- Note: Simplified pipeline leveraging AI for interpretation and real-time data for accuracy. 