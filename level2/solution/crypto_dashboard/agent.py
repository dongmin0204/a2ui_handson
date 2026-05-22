from google.adk.agents import Agent
from .market_data import search_web, get_prices

root_agent = Agent(
    model="gemini-2.5-flash",
    name="crypto_dashboard",
    description="A cryptocurrency market assistant with web search and fallback price data.",
    instruction=(
        "You are a crypto market assistant. "
        "When users ask about cryptocurrency prices, trends, or market conditions:\n"
        "1. Use the search_web tool to search for real-time data "
        "(e.g. 'Bitcoin price today USD', 'crypto market overview today').\n"
        "2. If search_web fails or returns an error, use get_prices as a fallback "
        "for structured market data.\n"
        "3. Provide a clear summary highlighting:\n"
        "   - Current prices for requested coins\n"
        "   - Notable price movements (biggest gainers/losers)\n"
        "   - Overall market sentiment\n"
        "Always cite your data source (web search or fallback data)."
    ),
    tools=[search_web, get_prices],
)
