import json
import os
from google import genai
from google.genai import types

# 실시간 검색이 실패할 때 사용할 모의 데이터
MOCK_MARKET = [
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "price_usd": 107250.42,
        "change_24h_pct": 2.35,
        "market_cap_usd": 2_130_000_000_000,
        "volume_24h_usd": 38_500_000_000,
        "high_24h": 108_900.00,
        "low_24h": 104_100.00,
    },
    # ... (나머지 코인은 solution 참고)
]


def search_web(query: str) -> str:
    """Search the web via Gemini with Google Search grounding.

    Args:
        query: The search query (e.g. "Bitcoin price today USD")

    Returns:
        A string with search-grounded answer from Gemini.
        The agent should use this to answer the user's question.
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        return json.dumps({"error": "GOOGLE_API_KEY not set", "fallback": "Use get_prices instead"})

    # TODO: Gemini + Google Search grounding을 호출하세요.
    # 힌트:
    #   client = genai.Client(api_key=api_key)
    #   response = client.models.generate_content(
    #       model="gemini-2.5-flash",
    #       contents=query,
    #       config=types.GenerateContentConfig(
    #           tools=[types.Tool(google_search=types.GoogleSearch())],
    #       ),
    #   )
    #   return response.text
    return json.dumps({"error": "not implemented"})


def get_prices() -> list[dict]:
    """Get cryptocurrency market data for top 5 coins (static fallback).

    Returns a list of coins with price, change, market cap, volume, and range.
    Use this when search_web is unavailable.
    """
    return MOCK_MARKET
