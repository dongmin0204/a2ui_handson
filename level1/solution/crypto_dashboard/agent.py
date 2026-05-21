from google.adk.agents import Agent
from google.adk.models.anthropic_llm import AnthropicLlm

root_agent = Agent(
    model=AnthropicLlm(model="claude-sonnet-4-5-20250929"),
    name="crypto_dashboard",
    description="A cryptocurrency market assistant.",
    instruction=(
        "You are a crypto market assistant. "
        "Users will ask about cryptocurrency prices and market trends. "
        "Answer based on your knowledge. "
        "Be honest when you don't have real-time data."
    ),
)
