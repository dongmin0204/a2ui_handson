from google.adk.agents import Agent
from .market_data import search_web, get_prices

# TODO: 에이전트에 도구(Tool)를 추가하세요.
# - tools에 search_web (웹 검색)과 get_prices (폴백 데이터)를 등록
# - instruction에서 search_web을 우선 사용하고, 실패 시 get_prices를 쓰도록 지시

root_agent = Agent(
    model="gemini-2.5-flash",
    name="crypto_dashboard",
    description="...",  # TODO
    instruction="...",  # TODO: search_web 우선, get_prices 폴백 지시 포함
    # TODO: tools=[...] 추가
)
