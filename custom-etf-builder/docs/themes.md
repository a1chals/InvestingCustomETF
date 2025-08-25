# Theme Discovery (Dynamic via Perplexity + GPT-4o)

## Approach
- **Dynamic Discovery**: No static theme taxonomy - GPT-4o identifies themes from user input
- **Real-time Data**: Perplexity API finds relevant companies and market data for any theme
- **Flexible Mapping**: Can handle emerging trends, niche sectors, or user-specific observations

## Example Theme Identification

User input: *"I think EV fleets will explode. I see a lot of chargers popping up."*

GPT-4o identifies:
- Primary theme: `electric_vehicles` (confidence: 0.9)
- Secondary theme: `charging_infrastructure` (confidence: 0.8)

Perplexity then dynamically finds:
- Relevant companies: TSLA, CHPT, EVgo, ChargePoint, etc.
- Market data: Current prices, market caps, sector classifications
- Context: Recent news, growth trends, competitive landscape

## Benefits Over Static Lists
- **Always Current**: No need to manually update allowlists
- **Comprehensive Coverage**: Can handle any user-mentioned theme or trend
- **Context-Aware**: Real-time market conditions inform recommendations
- **Scalable**: Works for mainstream and niche investment themes alike

## Quality Controls
- Confidence thresholds for theme detection (≥ 0.7 recommended)
- Market cap and liquidity filters applied via Perplexity data
- Sector concentration limits enforced by policy engine
- Human-readable rationale required for each allocation 