from google.adk.agents import Agent
from google.adk.models.anthropic_llm import AnthropicLlm
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .market_data import get_prices
from .a2ui_utils import a2ui_callback

# TODO 1: A2uiSchemaManager를 생성하세요.
# 힌트: version="0.8", catalogs=[BasicCatalog.get_config("0.8")]

schema_manager = ...  # TODO

# TODO 2: generate_system_prompt()로 A2UI 지시문을 생성하세요.
# 힌트: role_description, workflow_description, ui_description,
#        include_schema=True, include_examples=True

instruction = ...  # TODO

# TODO 3: Agent에 after_model_callback을 연결하세요.
root_agent = Agent(
    model=AnthropicLlm(model="claude-sonnet-4-5-20250929"),
    name="crypto_dashboard",
    description="A crypto market assistant that renders rich A2UI dashboards.",
    instruction=instruction,
    tools=[get_prices],
    # TODO: after_model_callback=a2ui_callback 추가
)
