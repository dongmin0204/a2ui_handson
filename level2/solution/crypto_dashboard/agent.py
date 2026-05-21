from google.adk.agents import Agent
from google.adk.models.anthropic_llm import AnthropicLlm
from .market_data import get_prices

root_agent = Agent(
    model=AnthropicLlm(model="claude-sonnet-4-5-20250929"),
    name="crypto_dashboard",
    description="A cryptocurrency market assistant with real-time price data.",
    instruction=(
        "You are a crypto market assistant with access to real-time market data. "
        "When users ask about cryptocurrency prices, trends, or market conditions, "
        "ALWAYS use the get_prices tool first to fetch current data. "
        "Never guess prices — always call the tool. "
        "After getting the data, provide a clear summary highlighting: "
        "1) Notable price movements (biggest gainers/losers) "
        "2) Overall market sentiment "
        "3) Any coins with significant volume changes"
    ),
    tools=[get_prices],
)
