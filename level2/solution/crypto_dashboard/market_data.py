import json
import os
from google import genai
from google.genai import types

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
    {
        "symbol": "ETH",
        "name": "Ethereum",
        "price_usd": 2534.18,
        "change_24h_pct": -1.28,
        "market_cap_usd": 305_000_000_000,
        "volume_24h_usd": 15_200_000_000,
        "high_24h": 2610.00,
        "low_24h": 2488.00,
    },
    {
        "symbol": "SOL",
        "name": "Solana",
        "price_usd": 172.55,
        "change_24h_pct": 5.12,
        "market_cap_usd": 84_000_000_000,
        "volume_24h_usd": 4_800_000_000,
        "high_24h": 175.30,
        "low_24h": 163.20,
    },
    {
        "symbol": "XRP",
        "name": "XRP",
        "price_usd": 2.38,
        "change_24h_pct": -0.45,
        "market_cap_usd": 138_000_000_000,
        "volume_24h_usd": 3_200_000_000,
        "high_24h": 2.42,
        "low_24h": 2.31,
    },
    {
        "symbol": "ADA",
        "name": "Cardano",
        "price_usd": 0.782,
        "change_24h_pct": 3.67,
        "market_cap_usd": 28_000_000_000,
        "volume_24h_usd": 890_000_000,
        "high_24h": 0.795,
        "low_24h": 0.748,
    },
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

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        return response.text
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_prices() -> list[dict]:
    """Get cryptocurrency market data for top 5 coins (static fallback).

    Returns a list of coins with price, change, market cap, volume, and range.
    Use this when search_web is unavailable.
    """
    return MOCK_MARKET
