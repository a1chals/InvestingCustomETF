# Vendors (MVP)

Primary: Perplexity API (real-time market data, company information, stock prices, market cap, sector data).  
Env var: PERPLEXITY_API_KEY

Secondary: OpenAI GPT-4o (sentiment analysis, portfolio reasoning, allocation logic).  
Env var: OPENAI_API_KEY

Notes:
- Perplexity provides real-time market insights, eliminating need for local data pipeline.
- GPT-4o focuses on reasoning and structured JSON output generation.
- Cache Perplexity results to handle rate limits efficiently.
- Real-time data ensures portfolio recommendations stay current. 