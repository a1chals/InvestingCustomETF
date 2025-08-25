# Simplified Risk Policy (Deterministic)

Baseline allocation guidelines by risk tier:

| Risk Level | Max Theme Exposure | Max Single Stock | Min Diversification | Portfolio Style |
|------------|-------------------|------------------|-------------------|-----------------|
| low        | 20%               | 5%               | 70% broad ETFs    | Conservative, large-cap focused |
| medium     | 40%               | 8%               | 50% broad ETFs    | Balanced growth and stability |
| high       | 60%               | 12%              | 30% broad ETFs    | Aggressive, growth-oriented |

### Policy Enforcement
- **Theme Exposure**: Total allocation to user-identified themes (e.g., EV, cybersecurity)
- **Single Stock Cap**: Maximum weight for any individual stock position  
- **Diversification Floor**: Minimum allocation to broad market ETFs (VTI, VT, etc.)
- **Position Minimum**: At least 2% allocation to make position meaningful
- **Sector Concentration**: No more than 25% in any single sector (enforced by GPT-4o)

### GPT-4o Integration
- AI applies these constraints during portfolio generation
- Policy rules are embedded in the GPT-4o prompt for consistent enforcement
- Real-time Perplexity data helps validate sector classifications and market caps
- Simpler rule set enables more reliable AI compliance than complex nested constraints 