from google.adk.agents import Agent
from google.adk.models.anthropic_llm import AnthropicLlm
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .market_data import get_prices
from .a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a crypto market assistant. When users ask about cryptocurrency "
        "prices or market conditions, use the get_prices tool to fetch current data."
    ),
    workflow_description=(
        "1. Call get_prices to fetch live market data. "
        "2. Analyze the data for trends. "
        "3. Return a structured A2UI dashboard."
    ),
    ui_description=(
        "Build a dashboard layout: "
        "- Top row: a heading Text with market summary. "
        "- For each coin, create a Card containing: "
        "  - Text with coin name and symbol (usageHint: heading2) "
        "  - Text with current price formatted as currency "
        "  - Icon: trending_up (green) if change_24h_pct > 0, trending_down (red) if < 0 "
        "  - Text with 24h change percentage "
        "  - Text with 24h high/low range "
        "- Use Row and Column components for grid layout. "
        "- Do NOT use markdown formatting in text values. "
        "- Respond ONLY with the A2UI JSON array. "
        "- Put all explanations into Text components."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    model=AnthropicLlm(model="claude-sonnet-4-5-20250929"),
    name="crypto_dashboard",
    description="A crypto market assistant that renders rich A2UI dashboards.",
    instruction=instruction,
    tools=[get_prices],
    after_model_callback=a2ui_callback,
)
