from google.adk.agents import Agent
from google.adk.models.anthropic_llm import AnthropicLlm
from .market_data import get_prices

# TODO: Lab 1의 에이전트에 도구(Tool)를 추가하세요.
# - tools 파라미터에 get_prices 함수를 등록
# - instruction을 수정하여 "반드시 도구를 먼저 호출" 하도록 지시

root_agent = Agent(
    model=AnthropicLlm(model="claude-sonnet-4-5-20250929"),
    name="crypto_dashboard",
    description="...",  # TODO
    instruction="...",  # TODO: 도구를 사용하라는 지시 포함
    # TODO: tools=[...] 추가
)
