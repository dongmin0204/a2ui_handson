import json
import urllib.request
import urllib.error

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

COIN_IDS = "bitcoin,ethereum,solana,ripple,cardano"
SYMBOL_MAP = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "ripple": "XRP",
    "cardano": "ADA",
}


def get_prices() -> list[dict]:
    """Get current cryptocurrency market data for top 5 coins.

    Returns a list of coins, each with:
    - symbol: ticker (BTC, ETH, etc.)
    - name: full name
    - price_usd: current price in USD
    - change_24h_pct: 24-hour price change percentage
    - market_cap_usd: market capitalization in USD
    - volume_24h_usd: 24-hour trading volume in USD
    - high_24h / low_24h: 24-hour price range

    Fetches live data from CoinGecko API. Falls back to mock data on failure.
    """
    try:
        url = (
            "https://api.coingecko.com/api/v3/coins/markets"
            f"?vs_currency=usd&ids={COIN_IDS}&order=market_cap_desc"
        )
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        return [
            {
                "symbol": SYMBOL_MAP.get(c["id"], c["symbol"].upper()),
                "name": c["name"],
                "price_usd": c["current_price"],
                "change_24h_pct": round(c.get("price_change_percentage_24h") or 0, 2),
                "market_cap_usd": c.get("market_cap", 0),
                "volume_24h_usd": c.get("total_volume", 0),
                "high_24h": c.get("high_24h", 0),
                "low_24h": c.get("low_24h", 0),
            }
            for c in data
        ]
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return MOCK_MARKET
